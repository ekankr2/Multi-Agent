import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from config.database.session import Base, get_db
from app.user.domain.user import User
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl


@pytest.fixture
def db_session():
    """테스트용 인메모리 SQLite 데이터베이스 세션"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False}  # Allow multi-threading for tests
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def client(db_session):
    """FastAPI TestClient with overridden database dependency"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """테스트용 사용자 생성"""
    repository = UserRepositoryImpl(db_session)
    user = User(
        google_id="google_test_123",
        email="testuser@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )
    return repository.save(user)


def test_get_me_endpoint_authenticated(client, test_user):
    """GET /user/me - 인증된 사용자 정보 조회 성공"""
    # TODO: For now, we'll need to mock authentication
    # When: GET /user/me 요청 (인증된 사용자로)
    response = client.get(
        "/user/me",
        # This will need to be replaced with proper session-based auth
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 사용자 정보가 정상적으로 반환됨
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
    assert data["name"] == test_user.name
    assert data["profile_picture"] == test_user.profile_picture
    assert "google_id" not in data  # google_id는 민감 정보이므로 응답에 포함하지 않음
    assert "created_at" in data
    assert "updated_at" in data


def test_get_me_endpoint_unauthenticated(client):
    """GET /user/me - 인증되지 않은 요청 시 401 에러"""
    # When: GET /user/me 요청 (인증 헤더 없이)
    response = client.get("/user/me")

    # Then: 401 Unauthorized 에러 반환
    assert response.status_code == 401
