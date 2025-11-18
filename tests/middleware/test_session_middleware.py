import pytest
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.middleware.session_validation import SessionValidationMiddleware


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    return Mock()


def get_current_user_id(request):
    """Dependency to extract user_id from request.state"""
    return request.state.user_id


@pytest.fixture
def test_app(mock_redis):
    """Test FastAPI app with session middleware"""
    from fastapi import Request

    app = FastAPI()

    # Add session validation middleware
    app.add_middleware(SessionValidationMiddleware, redis_client=mock_redis)

    # Test endpoint that requires authentication
    @app.get("/protected")
    async def protected_route(request: Request):
        user_id = request.state.user_id
        return {"user_id": user_id, "message": "success"}

    return app, mock_redis


def test_session_middleware_valid_session(test_app):
    """유효한 세션으로 요청 시 user_id 컨텍스트에 주입"""
    app, mock_redis = test_app
    client = TestClient(app)

    # Given: 유효한 세션이 Redis에 존재
    session_id = "valid-session-123"
    user_id = "42"
    mock_redis.get.return_value = user_id

    # When: 세션 쿠키와 함께 보호된 엔드포인트 요청
    response = client.get("/protected", cookies={"session_id": session_id})

    # Then: 요청 성공하고 user_id가 주입됨
    assert response.status_code == 200
    assert response.json() == {"user_id": 42, "message": "success"}
    mock_redis.get.assert_called_once_with(session_id)


def test_session_middleware_invalid_session(test_app):
    """유효하지 않은 세션 토큰 시 401 에러"""
    app, mock_redis = test_app
    client = TestClient(app)

    # Given: Redis에 존재하지 않는 세션
    session_id = "invalid-session-456"
    mock_redis.get.return_value = None

    # When: 잘못된 세션 쿠키로 요청
    response = client.get("/protected", cookies={"session_id": session_id})

    # Then: 401 Unauthorized 반환
    assert response.status_code == 401
    assert "Invalid or expired session" in response.json()["detail"]


def test_session_middleware_missing_session(test_app):
    """세션 쿠키 없이 요청 시 401 에러"""
    app, mock_redis = test_app
    client = TestClient(app)

    # When: 세션 쿠키 없이 요청
    response = client.get("/protected")

    # Then: 401 Unauthorized 반환
    assert response.status_code == 401
    assert "No session provided" in response.json()["detail"]


def test_session_middleware_expired_session(test_app):
    """만료된 세션 시 401 에러"""
    app, mock_redis = test_app
    client = TestClient(app)

    # Given: Redis에서 세션이 만료됨 (None 반환)
    session_id = "expired-session-789"
    mock_redis.get.return_value = None

    # When: 만료된 세션으로 요청
    response = client.get("/protected", cookies={"session_id": session_id})

    # Then: 401 Unauthorized 반환
    assert response.status_code == 401
    assert "Invalid or expired session" in response.json()["detail"]