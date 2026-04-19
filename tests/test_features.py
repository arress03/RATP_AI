from datetime import datetime

import polars as pl

from src.features.target import build_line_status, build_target
from src.features.temporal import add_temporal_features
from src.features.traffic import add_lag_features

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_calls(rows: list[dict]) -> pl.DataFrame:
    """Cree un DataFrame de metro_calls synthetique."""
    return pl.DataFrame(rows).with_columns(pl.col("fetched_at").cast(pl.Datetime))


def make_status(rows: list[dict]) -> pl.DataFrame:
    """Cree un DataFrame deja agrege (sortie de build_line_status)."""
    df = pl.DataFrame(rows).with_columns(pl.col("fetched_at").cast(pl.Datetime))
    # S'assurer que les types sont corrects
    if "has_disruption" in df.columns:
        df = df.with_columns(pl.col("has_disruption").cast(pl.Boolean))
    if "pct_delayed" in df.columns:
        df = df.with_columns(pl.col("pct_delayed").cast(pl.Float64))
    return df


# ---------------------------------------------------------------------------
# Tests build_line_status
# ---------------------------------------------------------------------------

def test_build_line_status_aggregation():
    """Verifie que l'agregation par (fetched_at, line) est correcte."""
    df = make_calls([
        {"fetched_at": datetime(2026, 4, 1, 8, 0), "line": "1", "is_delayed": False},
        {"fetched_at": datetime(2026, 4, 1, 8, 0), "line": "1", "is_delayed": True},
        {"fetched_at": datetime(2026, 4, 1, 8, 0), "line": "1", "is_delayed": True},
        {"fetched_at": datetime(2026, 4, 1, 8, 0), "line": "4", "is_delayed": False},
    ])
    result = build_line_status(df)

    line1 = result.filter(pl.col("line") == "1").row(0, named=True)
    line4 = result.filter(pl.col("line") == "4").row(0, named=True)

    assert line1["n_calls"] == 3
    assert line1["n_delayed"] == 2
    assert abs(line1["pct_delayed"] - 2 / 3) < 1e-9
    assert line1["has_disruption"] is True

    assert line4["n_calls"] == 1
    assert line4["n_delayed"] == 0
    assert line4["pct_delayed"] == 0.0
    assert line4["has_disruption"] is False


def test_build_line_status_no_delays():
    """Quand aucun appel n'est en retard, has_disruption doit etre False."""
    df = make_calls([
        {"fetched_at": datetime(2026, 4, 1, 8, 0), "line": "1", "is_delayed": False},
        {"fetched_at": datetime(2026, 4, 1, 8, 0), "line": "1", "is_delayed": False},
    ])
    result = build_line_status(df)
    row = result.row(0, named=True)
    assert row["has_disruption"] is False
    assert row["pct_delayed"] == 0.0


def test_build_line_status_multiple_timestamps():
    """Verifie que deux timestamps differents produisent deux lignes distinctes."""
    df = make_calls([
        {"fetched_at": datetime(2026, 4, 1, 8, 0), "line": "1", "is_delayed": False},
        {"fetched_at": datetime(2026, 4, 1, 8, 5), "line": "1", "is_delayed": True},
    ])
    result = build_line_status(df)
    assert len(result) == 2


# ---------------------------------------------------------------------------
# Tests build_target (anti-data-leakage)
# ---------------------------------------------------------------------------

def test_build_target_no_leakage_sort_order():
    """
    Le tri chronologique doit etre strict.
    On fournit les donnees dans le desordre et on verifie
    que le label y est calcule sur le futur, pas le passe.
    """
    # On fournit intentionnellement dans le mauvais ordre
    df = make_status([
        {"fetched_at": datetime(2026, 4, 1, 8, 10), "line": "1", "pct_delayed": 0.0, "n_calls": 2, "n_delayed": 0, "has_disruption": False},
        {"fetched_at": datetime(2026, 4, 1, 8, 0),  "line": "1", "pct_delayed": 0.5, "n_calls": 2, "n_delayed": 1, "has_disruption": True},
        {"fetched_at": datetime(2026, 4, 1, 8, 5),  "line": "1", "pct_delayed": 0.0, "n_calls": 2, "n_delayed": 0, "has_disruption": False},
    ])
    result = build_target(df, horizon_minutes=30)

    # Resultat doit etre trie chronologiquement
    timestamps = result["fetched_at"].to_list()
    assert timestamps == sorted(timestamps), "Le resultat n'est pas trie chronologiquement"


def test_build_target_future_only():
    """
    y=1 uniquement si la perturbation est dans le futur strict,
    pas sur le timestamp courant lui-meme.
    """
    df = make_status([
        # t=08:00 : perturbation MAINTENANT, mais pas dans le futur proche
        {"fetched_at": datetime(2026, 4, 1, 8, 0),  "line": "1", "pct_delayed": 1.0, "n_calls": 2, "n_delayed": 2, "has_disruption": True},
        # t=08:35 : pas de perturbation (hors horizon de 08:00 + 30min)
        {"fetched_at": datetime(2026, 4, 1, 8, 35), "line": "1", "pct_delayed": 0.0, "n_calls": 2, "n_delayed": 0, "has_disruption": False},
    ])
    result = build_target(df, horizon_minutes=30)

    row_t0 = result.filter(pl.col("fetched_at") == datetime(2026, 4, 1, 8, 0)).row(0, named=True)
    # 08:35 > 08:00 + 30min → hors fenetre → y=False
    assert row_t0["y"] is False


def test_build_target_positive_label():
    """y=1 quand une perturbation survient dans la fenetre future."""
    df = make_status([
        {"fetched_at": datetime(2026, 4, 1, 8, 0),  "line": "1", "pct_delayed": 0.0, "n_calls": 2, "n_delayed": 0, "has_disruption": False},
        {"fetched_at": datetime(2026, 4, 1, 8, 20), "line": "1", "pct_delayed": 1.0, "n_calls": 2, "n_delayed": 2, "has_disruption": True},
    ])
    result = build_target(df, horizon_minutes=30)

    row_t0 = result.filter(pl.col("fetched_at") == datetime(2026, 4, 1, 8, 0)).row(0, named=True)
    # 08:20 est dans (08:00, 08:30] → y=True
    assert row_t0["y"] is True


def test_build_target_no_cross_line_leakage():
    """Les perturbations d'une ligne ne doivent pas influencer le label d'une autre."""
    df = make_status([
        {"fetched_at": datetime(2026, 4, 1, 8, 0),  "line": "1", "pct_delayed": 0.0, "n_calls": 2, "n_delayed": 0, "has_disruption": False},
        {"fetched_at": datetime(2026, 4, 1, 8, 0),  "line": "4", "pct_delayed": 1.0, "n_calls": 2, "n_delayed": 2, "has_disruption": True},
        {"fetched_at": datetime(2026, 4, 1, 8, 15), "line": "1", "pct_delayed": 0.0, "n_calls": 2, "n_delayed": 0, "has_disruption": False},
        {"fetched_at": datetime(2026, 4, 1, 8, 15), "line": "4", "pct_delayed": 1.0, "n_calls": 2, "n_delayed": 2, "has_disruption": True},
    ])
    result = build_target(df, horizon_minutes=30)

    line1_t0 = result.filter((pl.col("line") == "1") & (pl.col("fetched_at") == datetime(2026, 4, 1, 8, 0))).row(0, named=True)
    line4_t0 = result.filter((pl.col("line") == "4") & (pl.col("fetched_at") == datetime(2026, 4, 1, 8, 0))).row(0, named=True)

    # Ligne 1 n'a pas de perturbation future → y=False
    assert line1_t0["y"] is False
    # Ligne 4 a une perturbation a t+15min → y=True
    assert line4_t0["y"] is True


# ---------------------------------------------------------------------------
# Tests add_lag_features
# ---------------------------------------------------------------------------

def test_lag_features_correct_shift():
    """lag_1 a t doit valoir pct_delayed a t-1 (snapshot precedent)."""
    df = make_status([
        {"fetched_at": datetime(2026, 4, 1, 8, 0),  "line": "1", "pct_delayed": 0.1, "n_calls": 2, "n_delayed": 0, "has_disruption": False},
        {"fetched_at": datetime(2026, 4, 1, 8, 5),  "line": "1", "pct_delayed": 0.5, "n_calls": 2, "n_delayed": 1, "has_disruption": True},
        {"fetched_at": datetime(2026, 4, 1, 8, 10), "line": "1", "pct_delayed": 0.8, "n_calls": 2, "n_delayed": 2, "has_disruption": True},
    ])
    result = add_lag_features(df, lags=[1])

    rows = result.sort("fetched_at").to_dicts()
    # t=08:00 : pas de precedent → None
    assert rows[0]["pct_delayed_lag_1"] is None
    # t=08:05 : lag_1 = valeur de t=08:00
    assert abs(rows[1]["pct_delayed_lag_1"] - 0.1) < 1e-9
    # t=08:10 : lag_1 = valeur de t=08:05
    assert abs(rows[2]["pct_delayed_lag_1"] - 0.5) < 1e-9


def test_lag_features_no_cross_line():
    """Le lag ne doit pas utiliser les valeurs d'une autre ligne."""
    df = make_status([
        {"fetched_at": datetime(2026, 4, 1, 8, 0), "line": "1", "pct_delayed": 0.9, "n_calls": 2, "n_delayed": 1, "has_disruption": True},
        {"fetched_at": datetime(2026, 4, 1, 8, 5), "line": "4", "pct_delayed": 0.0, "n_calls": 2, "n_delayed": 0, "has_disruption": False},
    ])
    result = add_lag_features(df, lags=[1])

    # Ligne 4 n'a qu'un seul snapshot → lag_1 doit etre None, pas 0.9
    row_4 = result.filter(pl.col("line") == "4").row(0, named=True)
    assert row_4["pct_delayed_lag_1"] is None


# ---------------------------------------------------------------------------
# Tests add_temporal_features
# ---------------------------------------------------------------------------

def test_temporal_peak_hour():
    """is_peak_hour doit etre True a 8h et 18h, False a 12h."""
    df = pl.DataFrame({
        "fetched_at": [
            datetime(2026, 4, 1, 8, 0),
            datetime(2026, 4, 1, 12, 0),
            datetime(2026, 4, 1, 18, 0),
        ]
    }).with_columns(pl.col("fetched_at").cast(pl.Datetime))

    result = add_temporal_features(df)
    rows = result.to_dicts()

    assert rows[0]["is_peak_hour"] is True   # 8h
    assert rows[1]["is_peak_hour"] is False  # 12h
    assert rows[2]["is_peak_hour"] is True   # 18h


def test_temporal_weekend():
    """is_weekend True le dimanche, False le lundi."""
    df = pl.DataFrame({
        "fetched_at": [
            datetime(2026, 3, 30, 10, 0),  # lundi
            datetime(2026, 4, 5, 10, 0),   # dimanche
        ]
    }).with_columns(pl.col("fetched_at").cast(pl.Datetime))

    result = add_temporal_features(df)
    rows = result.to_dicts()

    assert rows[0]["is_weekend"] is False
    assert rows[1]["is_weekend"] is True


def test_temporal_holiday():
    """is_holiday True le 1er mai (Fete du Travail)."""
    df = pl.DataFrame({
        "fetched_at": [
            datetime(2026, 5, 1, 10, 0),  # jour ferie
            datetime(2026, 5, 2, 10, 0),  # jour normal
        ]
    }).with_columns(pl.col("fetched_at").cast(pl.Datetime))

    result = add_temporal_features(df)
    rows = result.to_dicts()

    assert rows[0]["is_holiday"] is True
    assert rows[1]["is_holiday"] is False
