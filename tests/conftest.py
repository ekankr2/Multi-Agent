"""
Shared test fixtures for all tests.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.database.session import Base

# Import ORM models to register them with SQLAlchemy Base
from app.user.infrastructure.orm.user_orm import UserORM  # noqa: F401
from app.board.infrastructure.orm.board_orm import BoardORM  # noqa: F401


@pytest.fixture
def db_session():
    """테스트용 SQLite 데이터베이스 세션"""
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

    # Clean up test database file
    import os
    if os.path.exists("./test.db"):
        os.remove("./test.db")