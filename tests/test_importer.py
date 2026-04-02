from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db import init_db
from src.db.importer import import_all, import_snapshot
from src.db.models import MetroCall, Snapshot

SAMPLE_PATH = Path(__file__).parent.parent / "data" / "samples" / "sample_snapshot.json"


@pytest.fixture
def session():
    """Base SQLite en mémoire isolée pour chaque test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    init_db(engine)
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def test_import_snapshot_nominal(session):
    """Un snapshot valide doit créer 1 Snapshot et N MetroCall en base."""
    result = import_snapshot(SAMPLE_PATH, session)

    assert result is not None
    assert isinstance(result, Snapshot)

    snapshots = session.query(Snapshot).all()
    assert len(snapshots) == 1
    assert snapshots[0].total_calls == 8

    calls = session.query(MetroCall).all()
    assert len(calls) == 8


def test_import_snapshot_fields(session):
    """Les champs du snapshot doivent être correctement mappés."""
    import_snapshot(SAMPLE_PATH, session)

    snapshot = session.query(Snapshot).first()
    assert snapshot.fetched_at is not None
    assert snapshot.raw_file_path != ""

    delayed_calls = session.query(MetroCall).filter_by(is_delayed=True).all()
    assert len(delayed_calls) == 3

    lines = {c.line for c in session.query(MetroCall).all()}
    assert lines == {"1", "4", "13"}


def test_import_snapshot_deduplication(session):
    """Importer deux fois le même fichier ne doit pas créer de doublon."""
    first = import_snapshot(SAMPLE_PATH, session)
    second = import_snapshot(SAMPLE_PATH, session)

    assert first is not None
    assert second is None  # doublon détecté

    assert session.query(Snapshot).count() == 1
    assert session.query(MetroCall).count() == 8


def test_import_all(session, tmp_path):
    """import_all() doit importer tous les JSON du dossier."""
    import shutil

    # Copier le sample dans un dossier temporaire avec deux noms différents
    shutil.copy(SAMPLE_PATH, tmp_path / "snapshot_a.json")

    imported, skipped = import_all(tmp_path, session)

    assert imported == 1
    assert skipped == 0
    assert session.query(Snapshot).count() == 1


def test_import_all_skip_duplicates(session, tmp_path):
    """import_all() doit ignorer les fichiers déjà importés."""
    import shutil

    shutil.copy(SAMPLE_PATH, tmp_path / "snapshot_a.json")

    import_all(tmp_path, session)
    imported, skipped = import_all(tmp_path, session)  # deuxième passe

    assert imported == 0
    assert skipped == 1


def test_import_all_empty_dir(session, tmp_path):
    """import_all() sur un dossier vide doit retourner (0, 0)."""
    imported, skipped = import_all(tmp_path, session)
    assert imported == 0
    assert skipped == 0
