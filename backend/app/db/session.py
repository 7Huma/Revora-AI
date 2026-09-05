from contextlib import contextmanager
from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.database import SessionLocal


def get_session() -> Session:
    """
    Create and return a new database session.

    The caller is responsible for closing the session.
    """
    return SessionLocal()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """
    Provide a transactional database session.

    Commits when the operation succeeds.
    Rolls back if an exception occurs.
    Always closes the session.
    """
    db = SessionLocal()

    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()