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


def test_create_board_endpoint(client, test_user):
    """POST /board - 게시글 작성 성공"""
    # Given: 게시글 데이터
    board_data = {
        "title": "Test Board Title",
        "content": "Test board content"
    }

    # When: POST /board 요청 (인증된 사용자로)
    response = client.post(
        "/board",
        json=board_data,
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 게시글이 성공적으로 생성됨
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Board Title"
    assert data["content"] == "Test board content"
    assert data["user_id"] == test_user.id
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


def test_create_board_endpoint_unauthenticated(client):
    """POST /board - 인증 안 된 요청 시 401 에러"""
    # Given: 게시글 데이터
    board_data = {
        "title": "Test Board Title",
        "content": "Test board content"
    }

    # When: POST /board 요청 (인증 헤더 없이)
    response = client.post("/board", json=board_data)

    # Then: 401 Unauthorized 에러 반환
    assert response.status_code == 401


def test_create_board_endpoint_validation_error(client, test_user):
    """POST /board - 유효성 검증 실패 시 422 에러"""
    # Given: 잘못된 게시글 데이터 (제목이 너무 긺)
    board_data = {
        "title": "A" * 256,  # 256자 (최대 255자 초과)
        "content": "Test content"
    }

    # When: POST /board 요청
    response = client.post(
        "/board",
        json=board_data,
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 422 Validation Error 반환
    assert response.status_code == 422
