import numpy as np
import polars as pl


def build_line_status(df: pl.DataFrame) -> pl.DataFrame:
    """
    Agregation des metro_calls par (fetched_at, line).

    Colonnes produites :
    - n_calls       : nombre total d'appels sur la ligne
    - n_delayed     : nombre d'appels en retard
    - pct_delayed   : proportion d'appels en retard (0.0 a 1.0)
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


def _forward_any(times_ns: np.ndarray, disruptions: np.ndarray, horizon_ns: int) -> np.ndarray:
    """
    Calcul vectorise : pour chaque index i, y[i] = True si disruptions[j] == True
    pour au moins un j dans (i, last_j] ou times[last_j] <= times[i] + horizon_ns.

    Utilise un cumsum inverse + searchsorted pour eviter tout produit cartesien.
    Complexite O(n log n) au lieu de O(n^2).
    """
    n = len(times_ns)
    end_times = times_ns + horizon_ns

    # j_end[i] = premier index j tel que times[j] > times[i] + horizon (exclu)
    j_end = np.searchsorted(times_ns, end_times, side="right")

    # cumsum inverse : cumsum_r[i] = sum(disruptions[i:])
    cumsum_r = np.zeros(n + 1, dtype=np.int32)
    cumsum_r[:n] = np.cumsum(disruptions[::-1])[::-1]

    # Disruptions dans la fenetre (i, j_end[i]) = cumsum_r[i+1] - cumsum_r[j_end[i]]
    counts = cumsum_r[1:] - cumsum_r[j_end]
    return counts > 0


def build_target(df: pl.DataFrame, horizon_minutes: int = 30) -> pl.DataFrame:
    """
    Construit la variable cible binaire y pour chaque (fetched_at, line).

    y = True si une perturbation survient sur cette ligne dans les
    `horizon_minutes` minutes STRICTEMENT FUTURES apres fetched_at.

    Regles anti-data-leakage :
    - Tri chronologique strict avant toute operation
    - Fenetre strictement future : fetched_at < future_at <= fetched_at + horizon
    - Traitement par ligne pour eviter les fuites inter-lignes
    - Algorithme vectorise O(n log n) — pas de produit cartesien
    """
    df = df.sort(["line", "fetched_at"])
    horizon_ns = horizon_minutes * 60 * 1_000_000_000  # nanosecondes

    parts = []
    for line in df["line"].unique().sort().to_list():
        line_df = df.filter(pl.col("line") == line).sort("fetched_at")

        times_ns = line_df["fetched_at"].cast(pl.Int64).to_numpy()
        disruptions = line_df["has_disruption"].cast(pl.Int32).to_numpy()

        y = _forward_any(times_ns, disruptions, horizon_ns)
        parts.append(line_df.with_columns(pl.Series("y", y)))

    return pl.concat(parts).sort(["line", "fetched_at"])
