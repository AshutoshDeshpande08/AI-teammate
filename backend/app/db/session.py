"""
Database engine + session setup.

This is the single source of truth for the SQLAlchemy `Base` class,
the `engine`, and the `SessionLocal` factory. Models import `Base`
from here; the API layer imports `get_db` as a FastAPI dependency.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# SQLite needs this flag when used from multiple threads (FastAPI's
# default dev server uses a thread pool). Ignored for other databases.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables if they don't exist yet.

    Models must be imported before calling create_all() so that
    SQLAlchemy knows about them via Base.metadata.
    """
    from app.models import customer, ticket  # noqa: F401  (registers models)

    Base.metadata.create_all(bind=engine)
