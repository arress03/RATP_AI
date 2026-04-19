import polars as pl

# ---------------------------------------------------------------------------
# Features utilisees par tous les modeles — source unique de verite
# ---------------------------------------------------------------------------

FEATURE_COLS = [
    # Temporelles
    "hour",
    "day_of_week",
    "is_weekend",
    "is_holiday",
    "is_peak_hour",
    "month",
    "week_of_year",
    # Lags (5min, 15min, 30min)
    "pct_delayed_lag_1",
    "pct_delayed_lag_3",
    "pct_delayed_lag_6",
    "has_disruption_lag_1",
    "has_disruption_lag_3",
    "has_disruption_lag_6",
    # Rolling (30min, 1h)
    "pct_delayed_rolling_6",
    "pct_delayed_rolling_12",
    # Volume
    "n_calls",
]


def temporal_split(df: pl.DataFrame, train_ratio: float = 0.70, val_ratio: float = 0.17):
    """
    Decoupage CHRONOLOGIQUE strict en 3 parties.
    JAMAIS de split aleatoire sur des series temporelles.

    Repartition par defaut :
      |--- 70% train ---|--- 17% validation ---|--- 13% test ---|
        jour 1->12           jour 13->15          jour 16->17

    Le tri par fetched_at garantit l'absence de data leakage :
    le modele ne voit jamais de donnees futures pendant l'entrainement.

    Retourne (X_train, X_val, X_test, y_train, y_val, y_test) sous forme
    de tableaux numpy compatibles scikit-learn / LightGBM.
    """
    # Tri chronologique strict — indispensable
    df = df.sort("fetched_at")

    n = len(df)
    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train = df[:train_end]
    val = df[train_end:val_end]
    test = df[val_end:]

    X_train = train.select(FEATURE_COLS).to_numpy()
    X_val = val.select(FEATURE_COLS).to_numpy()
    X_test = test.select(FEATURE_COLS).to_numpy()

    y_train = train["y"].cast(pl.Int8).to_numpy()
    y_val = val["y"].cast(pl.Int8).to_numpy()
    y_test = test["y"].cast(pl.Int8).to_numpy()

    print("Split chronologique :")
    print(f"  Train : {len(train):>6} lignes  ({train['fetched_at'].min()} -> {train['fetched_at'].max()})")
    print(f"  Val   : {len(val):>6} lignes  ({val['fetched_at'].min()} -> {val['fetched_at'].max()})")
    print(f"  Test  : {len(test):>6} lignes  ({test['fetched_at'].min()} -> {test['fetched_at'].max()})")
    print(f"  Taux positifs — train: {y_train.mean():.1%}  val: {y_val.mean():.1%}  test: {y_test.mean():.1%}")

    return X_train, X_val, X_test, y_train, y_val, y_test