import json
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.db.models import MetroCall, Snapshot


def _parse_dt(value: str | None) -> datetime | None:
    """Parse une chaine ISO 8601 en datetime aware UTC, ou None."""
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def import_snapshot(json_path: str | Path, session: Session) -> Snapshot | None:
    """
    Lit un fichier JSON de snapshot et l'insere en base.
    Retourne le Snapshot cree, ou None si deja importe (deduplication sur fetched_at).
    Gere les doublons de timestamp (deux fichiers avec le meme fetched_at).
    """
    json_path = Path(json_path)
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    fetched_at = _parse_dt(data["fetched_at"])

    # Deduplication : on verifie si ce fetched_at existe deja en base
    existing = session.query(Snapshot).filter_by(fetched_at=fetched_at).first()
    if existing is not None:
        return None

    raw_calls = data.get("metro_calls", [])

    snapshot = Snapshot(
        fetched_at=fetched_at,
        total_calls=len(raw_calls),
        raw_file_path=str(json_path.resolve()),
    )
    session.add(snapshot)

    try:
        session.flush()  # obtenir snapshot.id avant d'inserer les calls
    except IntegrityError:
        # Deux fichiers avec le meme fetched_at (race condition collecteur)
        session.rollback()
        return None

    for raw in raw_calls:
        call = MetroCall(
            snapshot_id=snapshot.id,
            line=raw.get("line", ""),
            stop=raw.get("stop", ""),
            departure_status=raw.get("departure_status", ""),
            arrival_status=raw.get("arrival_status", ""),
            is_delayed=bool(raw.get("is_delayed", False)),
            expected_departure=_parse_dt(raw.get("expected_departure")),
            aimed_departure=_parse_dt(raw.get("aimed_departure")),
        )
        session.add(call)

    session.commit()
    return snapshot


def import_all(raw_dir: str | Path, session: Session) -> tuple[int, int]:
    """
    Importe en batch tous les fichiers JSON du dossier raw_dir
    qui ne sont pas encore en base.
    Retourne (nb_importes, nb_ignores).
    """
    raw_dir = Path(raw_dir)
    if not raw_dir.exists():
        return 0, 0

    json_files = sorted(raw_dir.glob("*.json"))
    imported, skipped = 0, 0

    for path in json_files:
        result = import_snapshot(path, session)
        if result is None:
            skipped += 1
        else:
            imported += 1

    return imported, skipped
