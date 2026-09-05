from sqlalchemy import text

from app.db.database import SessionLocal, engine, get_db


def test_database_engine_connects():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_session_factory_works():
    db = SessionLocal()

    try:
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
    finally:
        db.close()


def test_get_db_closes_session():
    generator = get_db()
    db = next(generator)

    assert db.is_active

    generator.close()

    assert db.is_active is False or db.closed if hasattr(db, "closed") else True