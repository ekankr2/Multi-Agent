"""
User Domain Integration Tests

이 테스트들은 User Domain의 전체 플로우를 검증합니다:
- Use Case Layer
- Repository Layer
- Domain Layer
의 통합 동작을 확인합니다.
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from config.database.session import get_db
from app.user.domain.user import User
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from app.user.application.use_case.register_or_login_user import RegisterOrLoginUser
from app.user.application.use_case.get_user_by_id import GetUserById
from app.user.application.use_case.update_user_profile import UpdateUserProfile


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


def test_user_full_workflow(db_session):
    """사용자 등록 → 조회 → 프로필 수정 전체 플로우"""
    # Given: Repository와 Use Cases
    repository = UserRepositoryImpl(db_session)
    register_use_case = RegisterOrLoginUser(repository)
    get_user_use_case = GetUserById(repository)
    update_profile_use_case = UpdateUserProfile(repository)

    # When: 1. 새로운 사용자 등록 (Google 로그인)
    google_user_info = {
        "google_id": "google_integration_123",
        "email": "integration@example.com",
        "name": "Integration Test User",
        "profile_picture": "https://example.com/integration.jpg"
    }
    registered_user = register_use_case.execute(**google_user_info)

    # Then: 사용자가 정상적으로 등록됨
    assert registered_user.id is not None
    assert registered_user.google_id == "google_integration_123"
    assert registered_user.email == "integration@example.com"
    assert registered_user.name == "Integration Test User"
    assert registered_user.created_at is not None
    assert registered_user.last_login_at is not None

    # When: 2. 등록된 사용자 조회
    user_id = registered_user.id
    retrieved_user = get_user_use_case.execute(user_id)

    # Then: 조회된 정보가 등록된 정보와 일치함
    assert retrieved_user.id == registered_user.id
    assert retrieved_user.google_id == registered_user.google_id
    assert retrieved_user.email == registered_user.email
    assert retrieved_user.name == registered_user.name

    # When: 3. 프로필 수정 (이름 변경)
    new_name = "Updated Integration User"
    updated_user = update_profile_use_case.execute(user_id, new_name)

    # Then: 이름이 성공적으로 변경됨
    assert updated_user.id == user_id
    assert updated_user.name == new_name
    assert updated_user.updated_at > updated_user.created_at

    # When: 4. 수정된 정보 재조회
    final_user = get_user_use_case.execute(user_id)

    # Then: 수정된 이름이 반영되어 있음
    assert final_user.name == new_name
    assert final_user.email == "integration@example.com"  # 다른 정보는 그대로


def test_google_oauth_to_user_creation_flow(client, db_session, mock_redis):
    """Google OAuth 콜백 → User 생성 → 세션 생성 플로우"""
    # Given: Mock Google OAuth response
    mock_user_profile = {
        "sub": "google_oauth_integration_456",
        "email": "oauth_integration@gmail.com",
        "name": "OAuth Integration User",
        "picture": "https://lh3.googleusercontent.com/oauth.jpg"
    }

    # Mock the OAuth service to return fake data
    with patch('app.social_oauth.application.usecase.google_oauth2_usecase.GoogleOAuth2UseCase.login_and_fetch_user') as mock_login, \
         patch('app.social_oauth.infrastructure.service.google_oauth2_service.GoogleOAuth2Service.fetch_user_profile') as mock_fetch, \
         patch('app.social_oauth.adapter.input.web.google_oauth2_router.redis_client', mock_redis):

        from app.social_oauth.adapter.input.web.response.access_token import AccessToken
        mock_access_token = AccessToken(
            access_token="mock_access_token_integration",
            token_type="Bearer",
            expires_in=3600,
            refresh_token=None
        )
        mock_login.return_value = mock_access_token
        mock_fetch.return_value = mock_user_profile

        # When: 1. Google OAuth 콜백 호출
        response = client.get(
            "/authentication/google/redirect",
            params={"code": "fake_auth_code", "state": "fake_state"},
            follow_redirects=False
        )

        # Then: 리디렉션 응답 성공
        assert response.status_code == 307  # RedirectResponse

        # And: 2. User 엔티티가 자동 생성됨
        repository = UserRepositoryImpl(db_session)
        created_user = repository.find_by_google_id("google_oauth_integration_456")

        assert created_user is not None
        assert created_user.google_id == "google_oauth_integration_456"
        assert created_user.email == "oauth_integration@gmail.com"
        assert created_user.name == "OAuth Integration User"
        assert created_user.profile_picture == "https://lh3.googleusercontent.com/oauth.jpg"

        # And: 3. 세션 쿠키가 발급됨
        assert "session_id" in response.cookies
        session_id = response.cookies["session_id"]

        # And: 4. Redis에 세션이 저장됨
        stored_user_id = mock_redis.get(session_id)
        assert stored_user_id is not None
        assert int(stored_user_id) == created_user.id

        # And: 5. 발급된 세션으로 /user/me 조회 성공
        me_response = client.get(
            "/user/me",
            cookies={"session_id": session_id}
        )

        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["id"] == created_user.id
        assert user_data["email"] == "oauth_integration@gmail.com"
        assert user_data["name"] == "OAuth Integration User"