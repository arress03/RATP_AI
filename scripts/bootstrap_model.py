"""
Genere models/best_model.pkl si absent.
Sort toujours avec exit code 0 — uvicorn doit demarrer meme sans modele.
"""
import sys
from pathlib import Path

# Garantit que le repertoire racine du projet est dans sys.path
# quel que soit le repertoire de travail courant.
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

MODEL_PATH = ROOT / "models" / "best_model.pkl"

print("[bootstrap] Demarrage du script bootstrap_model.py", flush=True)
print(f"[bootstrap] Verification : {MODEL_PATH.resolve()}", flush=True)

if MODEL_PATH.exists():
    print(f"[bootstrap] Modele deja present -> {MODEL_PATH}", flush=True)
    sys.exit(0)

print("[bootstrap] Modele absent — generation d'un modele de secours...", flush=True)

try:
    print("[bootstrap] Import des dependances...", flush=True)
    import joblib
    import numpy as np
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import StandardScaler
    print("[bootstrap] Dependances importees.", flush=True)

    print("[bootstrap] Import de FEATURE_COLS...", flush=True)
    from src.models.train import FEATURE_COLS
    print(f"[bootstrap] {len(FEATURE_COLS)} features detectees.", flush=True)

    print("[bootstrap] Generation des donnees synthetiques...", flush=True)
    rng = np.random.default_rng(42)
    n = 2000
    X = rng.uniform(0, 1, size=(n, len(FEATURE_COLS)))
    y = (rng.uniform(size=n) < 0.30).astype(int)

    print("[bootstrap] Entrainement du modele de secours (LR)...", flush=True)
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)),
    ])
    pipeline.fit(X, y)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"[bootstrap] Modele de secours sauvegarde -> {MODEL_PATH}", flush=True)

except Exception as exc:
    print(f"[bootstrap] ERREUR lors de la generation du modele : {exc}", flush=True)
    print("[bootstrap] L'API demarrera sans modele (health: model_loaded=false).", flush=True)

print("[bootstrap] Script termine — lancement d'uvicorn.", flush=True)
sys.exit(0)
