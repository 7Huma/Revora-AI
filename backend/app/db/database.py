from collections.abc import Generator
from app.db.models import Base

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import settings


def _build_engine():
    """
    Create the SQLAlchemy engine.

    SQLite needs check_same_thread=False for FastAPI's request handling.
    PostgreSQL does not need this option.
    """
    connect_args = {}

    if settings.DATABASE_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


engine = _build_engine()

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI database dependency.

    Opens one database session for a request and guarantees
    that the session is closed afterward.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()