import polars as pl


def build_line_status(df: pl.DataFrame) -> pl.DataFrame:
    """
    Agrège les metro_calls par (fetched_at, line).

    Colonnes produites :
    - n_calls       : nombre total d'appels sur la ligne
    - n_delayed     : nombre d'appels en retard
    - pct_delayed   : proportion d'appels en retard (0.0 à 1.0)
    - has_disruption: True si au moins un appel est en retard
    """
    return (
        df.group_by(["fetched_at", "line"])
        .agg(
            pl.len().alias("n_calls"),
            pl.col("is_delayed").sum().alias("n_delayed"),
            (pl.col("is_delayed").sum() / pl.len()).alias("pct_delayed"),
            pl.col("is_delayed").any().alias("has_disruption"),
        )
        .sort(["line", "fetched_at"])
    )


def build_target(df: pl.DataFrame, horizon_minutes: int = 30) -> pl.DataFrame:
    """
    Construit la variable cible binaire y pour chaque (fetched_at, line).

    y = 1 si une perturbation (has_disruption=True) survient sur cette ligne
    dans les `horizon_minutes` minutes SUIVANT fetched_at.

    Règles anti-data-leakage :
    - Tri chronologique strict avant toute opération
    - La fenêtre est strictement future : fetched_at < future_at <= fetched_at + horizon
    - Groupby line pour éviter les fuites entre lignes
    """
    # Tri chronologique strict — indispensable
    df = df.sort(["line", "fetched_at"])

    # On prépare le côté "futur" du self-join
    future = df.select(["line", "fetched_at", "has_disruption"]).rename(
        {"fetched_at": "future_at", "has_disruption": "future_disruption"}
    )

    # Joint sur la même ligne, filtré sur la fenêtre temporelle future
    joined = (
        df.join(future, on="line", how="left")
        .filter(
            (pl.col("future_at") > pl.col("fetched_at"))
            & (
                pl.col("future_at")
                <= pl.col("fetched_at") + pl.duration(minutes=horizon_minutes)
            )
        )
        .group_by(["line", "fetched_at"])
        .agg(pl.col("future_disruption").any().alias("y"))
    )

    return (
        df.join(joined, on=["line", "fetched_at"], how="left")
        .with_columns(pl.col("y").fill_null(False))
        .sort(["line", "fetched_at"])
    )
