import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.user.domain.user import User
from app.user.infrastructure.orm.user_orm import UserORM  # Import to register the table
from config.database.session import Base


@pytest.fixture
def db_session():
    """테스트용 인메모리 SQLite 데이터베이스 세션"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


def test_user_repository_save(db_session):
    """UserRepository가 User를 데이터베이스에 저장"""
    from app.user.application.port.user_repository_port import UserRepositoryPort
    from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl

    # Given: User 엔티티 생성
    user = User(
        google_id="google_123456",
        email="test@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )

    # When: Repository를 통해 저장
    repository = UserRepositoryImpl(db_session)
    saved_user = repository.save(user)

    # Then: ID가 할당되고 저장됨
    assert saved_user.id is not None
    assert saved_user.google_id == "google_123456"
    assert saved_user.email == "test@example.com"
    assert saved_user.name == "Test User"
    assert saved_user.profile_picture == "https://example.com/photo.jpg"
    assert saved_user.created_at is not None
    assert saved_user.updated_at is not None
    assert saved_user.last_login_at is not None