from sqlalchemy import text

from app.db.session import get_session, session_scope


def test_get_session_works():
    db = get_session()

    try:
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        db.close()


def test_session_scope_commits():
    with session_scope() as db:
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_session_scope_handles_database_operations():
    with session_scope() as db:
        assert db.is_active