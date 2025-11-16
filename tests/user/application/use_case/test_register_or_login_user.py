import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

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


def test_register_or_login_user_new_user(db_session):
    """새로운 Google 사용자 자동 회원가입"""
    from app.user.application.use_case.register_or_login_user import RegisterOrLoginUser

    # Given: 새로운 Google 사용자 정보
    google_id = "google_new_user_123"
    email = "newuser@example.com"
    name = "New User"
    profile_picture = "https://example.com/new_photo.jpg"

    repository = UserRepositoryImpl(db_session)
    use_case = RegisterOrLoginUser(repository)

    # When: 새로운 사용자로 로그인 시도
    user = use_case.execute(
        google_id=google_id,
        email=email,
        name=name,
        profile_picture=profile_picture
    )

    # Then: 새로운 User가 생성되어 저장됨
    assert user is not None
    assert user.id is not None
    assert user.google_id == google_id
    assert user.email == email
    assert user.name == name
    assert user.profile_picture == profile_picture
    assert user.created_at is not None
    assert user.last_login_at is not None

    # 데이터베이스에 실제로 저장되었는지 확인
    saved_user = repository.find_by_google_id(google_id)
    assert saved_user is not None
    assert saved_user.id == user.id


def test_register_or_login_user_existing_user(db_session):
    """기존 사용자 로그인 시 last_login_at 갱신"""
    from app.user.application.use_case.register_or_login_user import RegisterOrLoginUser
    import time

    # Given: 이미 등록된 사용자
    google_id = "google_existing_user_456"
    email = "existing@example.com"
    name = "Existing User"
    profile_picture = "https://example.com/existing_photo.jpg"

    repository = UserRepositoryImpl(db_session)
    use_case = RegisterOrLoginUser(repository)

    # 첫 번째 로그인 (회원가입)
    first_login_user = use_case.execute(
        google_id=google_id,
        email=email,
        name=name,
        profile_picture=profile_picture
    )
    first_login_at = first_login_user.last_login_at

    # Wait a bit to ensure timestamp difference
    time.sleep(0.01)

    # When: 동일한 사용자가 다시 로그인
    second_login_user = use_case.execute(
        google_id=google_id,
        email=email,
        name=name,
        profile_picture=profile_picture
    )

    # Then: 기존 사용자가 반환되고 last_login_at이 갱신됨
    assert second_login_user is not None
    assert second_login_user.id == first_login_user.id
    assert second_login_user.google_id == google_id
    assert second_login_user.last_login_at > first_login_at

    # 데이터베이스에서 확인
    saved_user = repository.find_by_google_id(google_id)
    assert saved_user is not None
    assert saved_user.last_login_at > first_login_at