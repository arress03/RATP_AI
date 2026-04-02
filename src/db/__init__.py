import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from src.db.models import Base

_DEFAULT_DB_URL = "sqlite:///./data/metro.db"


def get_engine(db_url: str | None = None) -> Engine:
    url = db_url or os.getenv("DATABASE_URL", _DEFAULT_DB_URL)
    connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=connect_args)


def init_db(engine: Engine) -> None:
    """Crée toutes les tables si elles n'existent pas encore."""
    Base.metadata.create_all(engine)


def get_session_factory(engine: Engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
