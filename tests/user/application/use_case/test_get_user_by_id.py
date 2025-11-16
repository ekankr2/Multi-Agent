import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.user.domain.user import User
from app.user.infrastructure.orm.user_orm import UserORM
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
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


def test_get_user_by_id(db_session):
    """ID로 사용자 조회"""
    from app.user.application.use_case.get_user_by_id import GetUserById

    # Given: 사용자를 데이터베이스에 저장
    repository = UserRepositoryImpl(db_session)
    user = User(
        google_id="google_123456",
        email="test@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )
    saved_user = repository.save(user)

    # When: GetUserById use case로 사용자 조회
    use_case = GetUserById(repository)
    found_user = use_case.execute(saved_user.id)

    # Then: 저장된 사용자 정보가 반환됨
    assert found_user is not None
    assert found_user.id == saved_user.id
    assert found_user.google_id == "google_123456"
    assert found_user.email == "test@example.com"
    assert found_user.name == "Test User"
    assert found_user.profile_picture == "https://example.com/photo.jpg"