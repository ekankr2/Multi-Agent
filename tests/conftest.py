"""
Shared test fixtures for all tests.
"""
import pytest
from unittest.mock import Mock, patch
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


@pytest.fixture
def mock_redis():
    """Mock Redis client for session testing"""
    mock_redis_client = Mock()
    # Store sessions in a dict to simulate Redis
    mock_redis_client._sessions = {}

    def mock_get(session_id):
        return mock_redis_client._sessions.get(session_id)

    def mock_set(session_id, user_id, **kwargs):
        mock_redis_client._sessions[session_id] = str(user_id)
        return True

    mock_redis_client.get = mock_get
    mock_redis_client.set = mock_set

    # Patch get_redis to return our mock
    with patch('app.user.adapter.input.web.dependencies.get_redis', return_value=mock_redis_client):
        yield mock_redis_client


@pytest.fixture
def create_session_cookie(mock_redis):
    """Helper to create session cookies for testing"""
    def _create_session_cookie(user_id: int, session_id: str = "test-session"):
        """Create a session cookie for a given user_id"""
        mock_redis.set(session_id, str(user_id))
        return {"session_id": session_id}

    return _create_session_cookie