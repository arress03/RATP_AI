import pandas as pd
import polars as pl
from sqlalchemy import text

from src.db import get_engine
from src.features.target import build_line_status, build_target
from src.features.temporal import add_temporal_features
from src.features.traffic import add_lag_features, add_rolling_features

_QUERY = """
    SELECT
        s.fetched_at,
        c.line,
        c.is_delayed
    FROM metro_calls c
    JOIN snapshots s ON c.snapshot_id = s.id
    ORDER BY s.fetched_at, c.line
"""


def build_dataset(db_path: str, horizon_minutes: int = 30) -> pl.DataFrame:
    """
    Construit le DataFrame complet pret pour l'entrainement.

    Etapes :
    1. Charge les metro_calls depuis SQLite
    2. Agregation par (fetched_at, line) -> build_line_status()
    3. Features temporelles -> add_temporal_features()
    4. Features de lag -> add_lag_features()
    5. Features rolling -> add_rolling_features()
    6. Variable cible -> build_target()
    7. Suppression des lignes avec NaN (dues aux lags initiaux)

    Retourne un DataFrame Polars avec features + colonne cible y.
    """
    engine = get_engine(db_path if db_path.startswith("sqlite") else f"sqlite:///{db_path}")

    with engine.connect() as conn:
        pdf = pd.read_sql(text(_QUERY), conn)

    # Conversion pandas -> Polars (fetched_at en string, is_delayed en int dans SQLite)
    df = pl.from_pandas(pdf).with_columns(
        pl.col("fetched_at").str.to_datetime(format="%Y-%m-%d %H:%M:%S%.f", strict=False),
        pl.col("is_delayed").cast(pl.Boolean),
    )

    # 1. Agregation par (fetched_at, line)
    df = build_line_status(df)

    # 2. Features temporelles
    df = add_temporal_features(df)

    # 3. Features de lag (1, 3, 6 snapshots = 5min, 15min, 30min)
    df = add_lag_features(df, lags=[1, 3, 6])

    # 4. Features rolling (6, 12 snapshots = 30min, 1h)
    df = add_rolling_features(df, windows=[6, 12])

    # 5. Variable cible
    df = build_target(df, horizon_minutes=horizon_minutes)

    # 6. Suppression des NaN dus aux lags initiaux
    df = df.drop_nulls()

    return df
