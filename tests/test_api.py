from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from fastapi.testclient import TestClient

import src.api.main as api_module
from src.api.main import app

# ---------------------------------------------------------------------------
# Fixture : patche joblib.load pour que le lifespan charge un faux modele
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_model():
    """Patche joblib.load et MODEL_PATH pour injecter un faux modele."""
    fake = MagicMock()
    fake.predict_proba.return_value = np.array([[0.2, 0.8]])

    with patch("src.api.main.MODEL_PATH") as mock_path, patch("src.api.main.joblib.load", return_value=fake):
        mock_path.exists.return_value = True
        yield fake

    api_module._model = None


@pytest.fixture()
def client(mock_model):
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# GET /health
# ---------------------------------------------------------------------------

def test_health_model_loaded(client):
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True


def test_health_model_missing():
    with patch("src.api.main.MODEL_PATH") as mock_path:
        mock_path.exists.return_value = False
        with TestClient(app) as c:
            r = c.get("/health")
    assert r.status_code == 200
    assert r.json()["model_loaded"] is False


# ---------------------------------------------------------------------------
# POST /predict
# ---------------------------------------------------------------------------

VALID_PAYLOAD = {
    "line": "4",
    "hour": 8,
    "day_of_week": 1,
    "is_weekend": False,
    "is_holiday": False,
    "is_peak_hour": True,
    "month": 4,
    "week_of_year": 16,
    "pct_delayed_lag_1": 0.1,
    "pct_delayed_lag_3": 0.05,
    "pct_delayed_lag_6": 0.0,
    "has_disruption_lag_1": True,
    "has_disruption_lag_3": False,
    "has_disruption_lag_6": False,
    "pct_delayed_rolling_6": 0.08,
    "pct_delayed_rolling_12": 0.06,
    "n_calls": 42,
}


def test_predict_returns_valid_response(client):
    r = client.post("/predict", json=VALID_PAYLOAD)
    assert r.status_code == 200
    body = r.json()
    assert body["line"] == "4"
    assert 0.0 <= body["disruption_probability"] <= 1.0
    assert body["risk_level"] in ("low", "medium", "high")


def test_predict_high_risk_level(client):
    # mock renvoie 0.8 -> high
    r = client.post("/predict", json=VALID_PAYLOAD)
    assert r.json()["risk_level"] == "high"


def test_predict_503_when_no_model():
    with patch("src.api.main.MODEL_PATH") as mock_path:
        mock_path.exists.return_value = False
        with TestClient(app) as c:
            r = c.post("/predict", json=VALID_PAYLOAD)
    assert r.status_code == 503


def test_predict_missing_field(client):
    payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "hour"}
    r = client.post("/predict", json=payload)
    assert r.status_code == 422


# ---------------------------------------------------------------------------
# GET /predict/all
# ---------------------------------------------------------------------------

def test_predict_all_returns_16_lines(client):
    r = client.get("/predict/all")
    assert r.status_code == 200
    body = r.json()
    assert len(body) == 16


def test_predict_all_fields(client):
    r = client.get("/predict/all")
    first = r.json()[0]
    assert "line" in first
    assert "disruption_probability" in first
    assert "risk_level" in first


def test_predict_all_503_when_no_model():
    with patch("src.api.main.MODEL_PATH") as mock_path:
        mock_path.exists.return_value = False
        with TestClient(app) as c:
            r = c.get("/predict/all")
    assert r.status_code == 503


# ---------------------------------------------------------------------------
# CORS headers
# ---------------------------------------------------------------------------

def test_cors_header_present(client):
    r = client.get("/health", headers={"Origin": "http://localhost:3000"})
    assert "access-control-allow-origin" in r.headers
