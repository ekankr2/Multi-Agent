import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time

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


def test_update_user_profile(db_session):
    """사용자 프로필 업데이트 (이름 변경)"""
    from app.user.application.use_case.update_user_profile import UpdateUserProfile

    # Given: 사용자를 데이터베이스에 저장
    repository = UserRepositoryImpl(db_session)
    user = User(
        google_id="google_123456",
        email="test@example.com",
        name="Original Name",
        profile_picture="https://example.com/photo.jpg"
    )
    saved_user = repository.save(user)
    original_updated_at = saved_user.updated_at

    # Wait a bit to ensure timestamp difference
    time.sleep(0.01)

    # When: UpdateUserProfile use case로 이름 변경
    use_case = UpdateUserProfile(repository)
    updated_user = use_case.execute(saved_user.id, "New Name")

    # Then: 이름이 변경되고 updated_at이 갱신됨
    assert updated_user is not None
    assert updated_user.id == saved_user.id
    assert updated_user.name == "New Name"
    assert updated_user.updated_at > original_updated_at

    # 데이터베이스에서 다시 조회하여 확인
    found_user = repository.find_by_id(saved_user.id)
    assert found_user is not None
    assert found_user.name == "New Name"
    assert found_user.updated_at > original_updated_at