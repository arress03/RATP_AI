from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = Path("models/best_model.pkl")

METRO_LINES = ["1", "2", "3", "3b", "4", "5", "6", "7", "7b", "8", "9", "10", "11", "12", "13", "14"]

_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model
    if MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
    else:
        _model = None
    yield
    _model = None


app = FastAPI(title="RATP AI", version="1.0.0", lifespan=lifespan)


class PredictRequest(BaseModel):
    line: str
    hour: int
    day_of_week: int
    is_weekend: bool
    is_holiday: bool
    is_peak_hour: bool
    month: int
    week_of_year: int
    pct_delayed_lag_1: float
    pct_delayed_lag_3: float
    pct_delayed_lag_6: float
    has_disruption_lag_1: bool
    has_disruption_lag_3: bool
    has_disruption_lag_6: bool
    pct_delayed_rolling_6: float
    pct_delayed_rolling_12: float
    n_calls: int


class PredictResponse(BaseModel):
    line: str
    disruption_probability: float
    risk_level: str


def _risk_level(proba: float) -> str:
    if proba >= 0.7:
        return "high"
    if proba >= 0.4:
        return "medium"
    return "low"


def _features_to_array(data: dict) -> np.ndarray:
    feature_cols = [
        "hour", "day_of_week", "is_weekend", "is_holiday", "is_peak_hour",
        "month", "week_of_year",
        "pct_delayed_lag_1", "pct_delayed_lag_3", "pct_delayed_lag_6",
        "has_disruption_lag_1", "has_disruption_lag_3", "has_disruption_lag_6",
        "pct_delayed_rolling_6", "pct_delayed_rolling_12",
        "n_calls",
    ]
    return np.array([[data[col] for col in feature_cols]], dtype=float)


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": _model is not None}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest):
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded — place best_model.pkl in models/")

    features = _features_to_array(request.model_dump())
    proba = float(_model.predict_proba(features)[0, 1])

    return PredictResponse(
        line=request.line,
        disruption_probability=round(proba, 4),
        risk_level=_risk_level(proba),
    )


@app.get("/predict/all", response_model=list[PredictResponse])
def predict_all():
    """
    Retourne une prediction par ligne avec des features neutres (heure actuelle, pas de trafic connu).
    Utile pour afficher un tableau de bord en temps reel sans historique.
    """
    if _model is None:
        raise HTTPException(status_code=503, detail="Model not loaded — place best_model.pkl in models/")

    from datetime import datetime, timezone

    import holidays as hol

    now = datetime.now(timezone.utc)
    fr_holidays = hol.France()
    is_holiday = now.date() in fr_holidays
    hour = now.hour
    dow = now.weekday()
    is_weekend = dow >= 5
    is_peak = hour in range(7, 10) or hour in range(17, 20)
    month = now.month
    week = now.isocalendar().week

    results = []
    for line in METRO_LINES:
        features = _features_to_array({
            "hour": hour,
            "day_of_week": dow,
            "is_weekend": int(is_weekend),
            "is_holiday": int(is_holiday),
            "is_peak_hour": int(is_peak),
            "month": month,
            "week_of_year": week,
            "pct_delayed_lag_1": 0.0,
            "pct_delayed_lag_3": 0.0,
            "pct_delayed_lag_6": 0.0,
            "has_disruption_lag_1": 0,
            "has_disruption_lag_3": 0,
            "has_disruption_lag_6": 0,
            "pct_delayed_rolling_6": 0.0,
            "pct_delayed_rolling_12": 0.0,
            "n_calls": 0,
        })
        proba = float(_model.predict_proba(features)[0, 1])
        results.append(PredictResponse(
            line=line,
            disruption_probability=round(proba, 4),
            risk_level=_risk_level(proba),
        ))

    return results
