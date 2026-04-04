import polars as pl


def add_lag_features(df: pl.DataFrame, lags: list[int] = [1, 3, 6]) -> pl.DataFrame:
    """
    Ajoute des features de lag pour chaque N snapshots passés (N * 5 minutes).

    Colonnes ajoutees par lag N :
    - pct_delayed_lag_N    : pct_delayed il y a N snapshots
    - has_disruption_lag_N : has_disruption il y a N snapshots

    Groupby line, tri chronologique strict avant shift.
    Les premieres N lignes par ligne auront des NaN (normal, supprimees ensuite).
    """
    df = df.sort(["line", "fetched_at"])

    lag_exprs = []
    for n in lags:
        lag_exprs += [
            pl.col("pct_delayed").shift(n).over("line").alias(f"pct_delayed_lag_{n}"),
            pl.col("has_disruption").shift(n).over("line").alias(f"has_disruption_lag_{n}"),
        ]

    return df.with_columns(lag_exprs)


def add_rolling_features(df: pl.DataFrame, windows: list[int] = [6, 12]) -> pl.DataFrame:
    """
    Ajoute des moyennes mobiles sur les N derniers snapshots.

    Colonnes ajoutees par fenetre N :
    - pct_delayed_rolling_N : moyenne de pct_delayed sur les N derniers snapshots

    Groupby line, tri chronologique strict.
    min_periods=1 pour eviter les NaN sur les premieres lignes.
    """
    df = df.sort(["line", "fetched_at"])

    rolling_exprs = [
        pl.col("pct_delayed")
        .rolling_mean(window_size=n, min_periods=1)
        .over("line")
        .alias(f"pct_delayed_rolling_{n}")
        for n in windows
    ]

    return df.with_columns(rolling_exprs)
