import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from unittest.mock import Mock

from app.user.adapter.input.web.dependencies import get_current_user
from app.user.domain.user import User


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_user_repository():
    """Mock UserRepository"""
    return Mock()


@pytest.fixture
def test_app():
    """Test FastAPI app with get_current_user dependency"""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(current_user: User = None):
        # We'll manually call get_current_user in tests
        return {"user_id": current_user.id, "email": current_user.email}

    return app


def test_get_current_user_from_session(mock_db):
    """세션에서 현재 사용자 조회"""
    # Given: request.state에 user_id가 주입된 상태
    mock_request = Mock(spec=Request)
    mock_request.state.user_id = 42

    # Given: 해당 user_id로 User가 DB에 존재
    from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
    from unittest.mock import patch

    expected_user = User(
        google_id="google123",
        email="test@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )
    expected_user.id = 42

    with patch.object(UserRepositoryImpl, 'find_by_id', return_value=expected_user):
        # When: get_current_user 호출
        # Note: The current implementation uses X-User-Id header, we need to refactor it
        # to use request.state.user_id from SessionValidationMiddleware
        from app.user.adapter.input.web.dependencies import get_current_user_from_session
        user = get_current_user_from_session(request=mock_request, db=mock_db)

        # Then: User 엔티티가 반환됨
        assert user.id == 42
        assert user.email == "test@example.com"
        assert user.name == "Test User"


def test_get_current_user_session_user_not_found(mock_db):
    """세션은 있지만 User가 DB에 없는 경우 예외 발생"""
    from fastapi import HTTPException
    from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
    from unittest.mock import patch

    # Given: request.state에 user_id가 주입된 상태
    mock_request = Mock(spec=Request)
    mock_request.state.user_id = 999

    # Given: 해당 user_id로 User가 DB에 없음
    with patch.object(UserRepositoryImpl, 'find_by_id', return_value=None):
        # When & Then: HTTPException 발생
        from app.user.adapter.input.web.dependencies import get_current_user_from_session
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_from_session(request=mock_request, db=mock_db)

        assert exc_info.value.status_code == 401
        assert "User not found" in exc_info.value.detail or "Unauthorized" in exc_info.value.detail