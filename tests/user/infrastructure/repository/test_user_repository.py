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


def test_user_repository_find_by_google_id(db_session):
    """google_id로 User 조회"""
    from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl

    # Given: User를 데이터베이스에 저장
    repository = UserRepositoryImpl(db_session)
    user = User(
        google_id="google_123456",
        email="test@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )
    saved_user = repository.save(user)

    # When: google_id로 조회
    found_user = repository.find_by_google_id("google_123456")

    # Then: 저장된 사용자가 조회됨
    assert found_user is not None
    assert found_user.id == saved_user.id
    assert found_user.google_id == "google_123456"
    assert found_user.email == "test@example.com"
    assert found_user.name == "Test User"
    assert found_user.profile_picture == "https://example.com/photo.jpg"


def test_user_repository_find_by_id(db_session):
    """id로 User 조회"""
    from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl

    # Given: User를 데이터베이스에 저장
    repository = UserRepositoryImpl(db_session)
    user = User(
        google_id="google_123456",
        email="test@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )
    saved_user = repository.save(user)

    # When: id로 조회
    found_user = repository.find_by_id(saved_user.id)

    # Then: 저장된 사용자가 조회됨
    assert found_user is not None
    assert found_user.id == saved_user.id
    assert found_user.google_id == "google_123456"
    assert found_user.email == "test@example.com"
    assert found_user.name == "Test User"
    assert found_user.profile_picture == "https://example.com/photo.jpg"