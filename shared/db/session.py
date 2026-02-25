from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base

Base = declarative_base()

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://user:password@localhost:5432/ki_rechnungsverarbeitung",
        )
        _engine = create_engine(database_url, echo=False, future=True)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            autocommit=False,
        )
    return _SessionLocal


def get_session():
    """
    FastAPI-kompatible DB-Session-Dependency:
    - Kann als Depends(get_session) verwendet werden.
    - Commit bei Erfolg, Rollback bei Exception.
    """
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
