import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient

from app.main import app
from config.database.session import get_db
from app.user.domain.user import User
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl


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


def test_google_oauth_callback_creates_user(client, db_session):
    """Google OAuth 콜백 시 User 자동 생성"""
    # Given: Mock Google OAuth response
    mock_user_profile = {
        "sub": "google_123456789",
        "email": "newuser@gmail.com",
        "name": "New User",
        "picture": "https://lh3.googleusercontent.com/a/photo.jpg"
    }

    # Mock the OAuth service to return fake data
    with patch('app.social_oauth.application.usecase.google_oauth2_usecase.GoogleOAuth2UseCase.login_and_fetch_user') as mock_login, \
         patch('app.social_oauth.infrastructure.service.google_oauth2_service.GoogleOAuth2Service.fetch_user_profile') as mock_fetch, \
         patch('app.social_oauth.adapter.input.web.google_oauth2_router.redis_client') as mock_redis:

        from app.social_oauth.adapter.input.web.response.access_token import AccessToken
        mock_access_token = AccessToken(
            access_token="mock_access_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token=None
        )
        mock_login.return_value = mock_access_token
        mock_fetch.return_value = mock_user_profile

        # When: Google OAuth 콜백 호출
        response = client.get(
            "/authentication/google/redirect",
            params={"code": "fake_auth_code", "state": "fake_state"},
            follow_redirects=False
        )

        # Then: 리디렉션 응답 성공
        assert response.status_code == 307  # RedirectResponse

        # And: 데이터베이스에 User가 생성됨
        repository = UserRepositoryImpl(db_session)
        user = repository.find_by_google_id("google_123456789")

        assert user is not None
        assert user.google_id == "google_123456789"
        assert user.email == "newuser@gmail.com"
        assert user.name == "New User"
        assert user.profile_picture == "https://lh3.googleusercontent.com/a/photo.jpg"


def test_google_oauth_callback_updates_last_login(client, db_session):
    """기존 User의 경우 last_login_at 갱신"""
    # Given: 기존 사용자가 데이터베이스에 존재
    repository = UserRepositoryImpl(db_session)
    existing_user = User(
        google_id="google_existing_123",
        email="existing@gmail.com",
        name="Existing User",
        profile_picture="https://lh3.googleusercontent.com/old.jpg"
    )
    saved_user = repository.save(existing_user)
    original_last_login = saved_user.last_login_at

    # Given: Mock Google OAuth response
    mock_user_profile = {
        "sub": "google_existing_123",
        "email": "existing@gmail.com",
        "name": "Existing User",
        "picture": "https://lh3.googleusercontent.com/old.jpg"
    }

    # Mock the OAuth service to return fake data
    with patch('app.social_oauth.application.usecase.google_oauth2_usecase.GoogleOAuth2UseCase.login_and_fetch_user') as mock_login, \
         patch('app.social_oauth.infrastructure.service.google_oauth2_service.GoogleOAuth2Service.fetch_user_profile') as mock_fetch, \
         patch('app.social_oauth.adapter.input.web.google_oauth2_router.redis_client') as mock_redis:

        from app.social_oauth.adapter.input.web.response.access_token import AccessToken
        mock_access_token = AccessToken(
            access_token="mock_access_token",
            token_type="Bearer",
            expires_in=3600,
            refresh_token=None
        )
        mock_login.return_value = mock_access_token
        mock_fetch.return_value = mock_user_profile

        # When: 기존 사용자가 Google OAuth로 재로그인
        response = client.get(
            "/authentication/google/redirect",
            params={"code": "fake_auth_code", "state": "fake_state"},
            follow_redirects=False
        )

        # Then: 리디렉션 응답 성공
        assert response.status_code == 307  # RedirectResponse

        # And: last_login_at이 갱신됨
        updated_user = repository.find_by_google_id("google_existing_123")
        assert updated_user is not None
        assert updated_user.last_login_at > original_last_login