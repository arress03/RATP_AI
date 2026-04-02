# Metro Disruption Predictor

Prédiction en temps réel des perturbations du métro parisien par ligne, alimentée par un modèle ML entraîné sur l'historique de l'API PRIM (Île-de-France Mobilités).

Dashboard live : **[https://metro-disruption-predictor.vercel.app](https://metro-disruption-predictor.vercel.app)** *(à venir)*

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VPS Hetzner                              │
│                                                                 │
│  ┌─────────────────┐          ┌──────────────────────────────┐  │
│  │  collector.py   │─────────▶│  data/raw/*.json             │  │
│  │  (systemd/5min) │          │  snapshots PRIM              │  │
│  └─────────────────┘          └──────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                         │
                                         │ import_all()
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Railway (API FastAPI)                       │
│                                                                 │
│  ┌──────────┐   ┌───────────────┐   ┌────────────────────────┐  │
│  │ SQLite / │──▶│ Feature       │──▶│ LightGBM / LogReg      │  │
│  │ Postgres │   │ Engineering   │   │ best_model.pkl         │  │
│  └──────────┘   └───────────────┘   └────────────────────────┘  │
│                                              │                  │
│  GET /predict/all ◀──────────────────────────┘                  │
│  GET /health                                                    │
│  POST /predict                                                  │
└─────────────────────────────────────────────────────────────────┘
                                         │
                                         │ polling 2min
                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Vercel (Next.js 14)                         │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Dashboard — 16 lignes × probabilité de perturbation    │   │
│   │  [ M1 ▓░░ 12% ] [ M2 ▓▓▓ 73% ] [ M3 ▓▓░ 45% ] ...     │   │
│   └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Stack

| Couche | Technologie |
|---|---|
| Collecte | Python 3.12 + schedule + API PRIM |
| Stockage | SQLite (dev) → PostgreSQL (prod) |
| Features | pandas, holidays |
| Modèles | scikit-learn, LightGBM |
| API | FastAPI + uvicorn |
| Frontend | Next.js 14 + Tailwind CSS |
| Déploiement API | Railway |
| Déploiement Frontend | Vercel |
| CI/CD | GitHub Actions |

---

## Installation

### Prérequis

- Python 3.12+
- Node.js 18+
- Clé API PRIM (Île-de-France Mobilités)

### Backend Python

```bash
# Cloner le repo
git clone https://github.com/<your-username>/metro-disruption-predictor.git
cd metro-disruption-predictor

# Installer les dépendances
make install

# Configurer l'environnement
cp .env.example .env
# Éditer .env avec ta clé IDFM_API_KEY
```

### Frontend Next.js

```bash
cd app
npm install
```

---

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `IDFM_API_KEY` | Clé API Île-de-France Mobilités | `abc123...` |
| `DATABASE_URL` | URL de la base de données | `sqlite:///./data/metro.db` |
| `ALLOWED_ORIGINS` | Origines CORS autorisées | `https://metro.vercel.app` |
| `NEXT_PUBLIC_API_URL` | URL de l'API FastAPI (frontend) | `https://metro-api.railway.app` |

---

## Commandes disponibles

```bash
# Installer les dépendances Python
make install

# Lancer le linter
make lint

# Lancer les tests
make test

# Démarrer le collecteur manuellement
make collect

# Démarrer l'API en développement
make api
# → http://localhost:8000
# → http://localhost:8000/docs (Swagger)

# Démarrer le frontend en développement
cd app && npm run dev
# → http://localhost:3000
```

---

## Structure du projet

```
metro-disruption-predictor/
├── .github/workflows/ci.yml   # CI GitHub Actions
├── data/
│   └── samples/               # Snapshot exemple pour les tests
├── notebooks/                 # Exploration, features, training
├── src/
│   ├── collector/             # Script de collecte PRIM (VPS)
│   ├── db/                    # Schéma SQLAlchemy + importeur
│   ├── features/              # Feature engineering
│   ├── models/                # Entraînement + évaluation
│   └── api/                   # FastAPI endpoints
├── app/                       # Next.js dashboard
└── tests/                     # Tests unitaires Python
```

---

## Données collectées

Le collecteur interroge l'endpoint `estimated-timetable` de l'API PRIM toutes les **5 minutes** pour les **16 lignes de métro** parisien (1, 2, 3, 3B, 4, 5, 6, 7, 7B, 8, 9, 10, 11, 12, 13, 14).

Chaque snapshot JSON contient :
- `fetched_at` — timestamp UTC de la collecte
- `metro_calls` — liste des appels avec statut de départ/arrivée, retard, arrêt, horaires visés et estimés

---

## Modèle ML

Le modèle prédit pour chaque ligne la **probabilité de perturbation dans les 30 prochaines minutes** (horizon configurable).

Features utilisées :
- **Temporelles** : heure, jour de semaine, week-end, jour férié, heures de pointe
- **Lags** : % de retards à t-5min, t-15min, t-30min
- **Rolling** : moyenne mobile sur 30min et 1h

Modèles entraînés : Logistic Regression (baseline) + **LightGBM** (meilleur modèle).

---

*Projet personnel — Données PRIM © Île-de-France Mobilités*
