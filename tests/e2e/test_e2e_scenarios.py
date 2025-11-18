"""
End-to-End Scenario Tests

이 테스트들은 전체 시스템의 엔드투엔드 시나리오를 검증합니다:
- Google OAuth → User Domain → Session → Board Domain
- 실제 사용자가 경험하는 완전한 플로우
"""
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app
from config.database.session import get_db
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from app.board.infrastructure.repository.board_repository_impl import BoardRepositoryImpl


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


def test_e2e_google_login_and_create_board(client, db_session, mock_redis):
    """Google 로그인 → 게시글 작성 → 목록 조회 전체 플로우"""
    # Given: Mock Google OAuth response
    mock_user_profile = {
        "sub": "google_e2e_user_123",
        "email": "e2e_user@gmail.com",
        "name": "E2E Test User",
        "picture": "https://lh3.googleusercontent.com/e2e.jpg"
    }

    # Mock the OAuth service to return fake data
    with patch('app.social_oauth.application.usecase.google_oauth2_usecase.GoogleOAuth2UseCase.login_and_fetch_user') as mock_login, \
         patch('app.social_oauth.infrastructure.service.google_oauth2_service.GoogleOAuth2Service.fetch_user_profile') as mock_fetch, \
         patch('app.social_oauth.adapter.input.web.google_oauth2_router.redis_client', mock_redis):

        from app.social_oauth.adapter.input.web.response.access_token import AccessToken
        mock_access_token = AccessToken(
            access_token="mock_access_token_e2e",
            token_type="Bearer",
            expires_in=3600,
            refresh_token=None
        )
        mock_login.return_value = mock_access_token
        mock_fetch.return_value = mock_user_profile

        # When: 1. Google OAuth 콜백 (사용자 로그인)
        oauth_response = client.get(
            "/authentication/google/redirect",
            params={"code": "fake_auth_code", "state": "fake_state"},
            follow_redirects=False
        )

        # Then: 리디렉션 응답 성공 및 세션 쿠키 발급
        assert oauth_response.status_code == 307
        assert "session_id" in oauth_response.cookies
        session_id = oauth_response.cookies["session_id"]

        # And: User가 자동 생성됨
        user_repository = UserRepositoryImpl(db_session)
        created_user = user_repository.find_by_google_id("google_e2e_user_123")
        assert created_user is not None
        assert created_user.email == "e2e_user@gmail.com"
        assert created_user.name == "E2E Test User"

        # And: Redis에 세션이 저장됨
        stored_user_id = mock_redis.get(session_id)
        assert stored_user_id is not None
        assert int(stored_user_id) == created_user.id

        # When: 2. 발급된 세션으로 게시글 작성
        board_data = {
            "title": "My First E2E Board",
            "content": "Created via E2E test from Google login"
        }
        create_board_response = client.post(
            "/board",
            json=board_data,
            cookies={"session_id": session_id}
        )

        # Then: 게시글이 성공적으로 생성됨
        assert create_board_response.status_code == 201
        created_board = create_board_response.json()
        assert created_board["title"] == "My First E2E Board"
        assert created_board["content"] == "Created via E2E test from Google login"
        assert created_board["user_id"] == created_user.id
        board_id = created_board["id"]

        # When: 3. 게시글 목록 조회
        list_response = client.get(
            "/board",
            cookies={"session_id": session_id}
        )

        # Then: 작성한 게시글이 목록에 포함됨
        assert list_response.status_code == 200
        board_list = list_response.json()
        assert len(board_list) >= 1

        # And: 작성한 게시글이 목록에 있고 작성자 정보가 일치함
        my_board = next((b for b in board_list if b["id"] == board_id), None)
        assert my_board is not None
        assert my_board["title"] == "My First E2E Board"
        assert "author" in my_board
        assert my_board["author"]["name"] == "E2E Test User"
        assert my_board["author"]["email"] == "e2e_user@gmail.com"


def test_e2e_multiple_users_board_interaction(client, db_session, mock_redis):
    """여러 사용자가 게시글 작성 및 각자 게시글 수정/삭제"""
    # Given: Mock Google OAuth responses for two users
    user_a_profile = {
        "sub": "google_e2e_user_a",
        "email": "user_a_e2e@gmail.com",
        "name": "User A E2E",
        "picture": "https://lh3.googleusercontent.com/user_a.jpg"
    }

    user_b_profile = {
        "sub": "google_e2e_user_b",
        "email": "user_b_e2e@gmail.com",
        "name": "User B E2E",
        "picture": "https://lh3.googleusercontent.com/user_b.jpg"
    }

    from app.social_oauth.adapter.input.web.response.access_token import AccessToken

    # When: 1. User A Google 로그인
    with patch('app.social_oauth.application.usecase.google_oauth2_usecase.GoogleOAuth2UseCase.login_and_fetch_user') as mock_login, \
         patch('app.social_oauth.infrastructure.service.google_oauth2_service.GoogleOAuth2Service.fetch_user_profile') as mock_fetch, \
         patch('app.social_oauth.adapter.input.web.google_oauth2_router.redis_client', mock_redis):

        mock_access_token = AccessToken(
            access_token="mock_token_user_a",
            token_type="Bearer",
            expires_in=3600,
            refresh_token=None
        )
        mock_login.return_value = mock_access_token
        mock_fetch.return_value = user_a_profile

        oauth_a_response = client.get(
            "/authentication/google/redirect",
            params={"code": "code_a", "state": "state_a"},
            follow_redirects=False
        )

        assert oauth_a_response.status_code == 307
        session_a = oauth_a_response.cookies["session_id"]

    # When: 2. User B Google 로그인
    with patch('app.social_oauth.application.usecase.google_oauth2_usecase.GoogleOAuth2UseCase.login_and_fetch_user') as mock_login, \
         patch('app.social_oauth.infrastructure.service.google_oauth2_service.GoogleOAuth2Service.fetch_user_profile') as mock_fetch, \
         patch('app.social_oauth.adapter.input.web.google_oauth2_router.redis_client', mock_redis):

        mock_access_token = AccessToken(
            access_token="mock_token_user_b",
            token_type="Bearer",
            expires_in=3600,
            refresh_token=None
        )
        mock_login.return_value = mock_access_token
        mock_fetch.return_value = user_b_profile

        oauth_b_response = client.get(
            "/authentication/google/redirect",
            params={"code": "code_b", "state": "state_b"},
            follow_redirects=False
        )

        assert oauth_b_response.status_code == 307
        session_b = oauth_b_response.cookies["session_id"]

    # Verify both users were created
    user_repository = UserRepositoryImpl(db_session)
    user_a = user_repository.find_by_google_id("google_e2e_user_a")
    user_b = user_repository.find_by_google_id("google_e2e_user_b")
    assert user_a is not None
    assert user_b is not None

    # When: 3. User A creates a board
    board_a_data = {
        "title": "User A's Board",
        "content": "Content by User A"
    }
    create_a_response = client.post(
        "/board",
        json=board_a_data,
        cookies={"session_id": session_a}
    )

    assert create_a_response.status_code == 201
    board_a = create_a_response.json()
    board_a_id = board_a["id"]
    assert board_a["user_id"] == user_a.id

    # When: 4. User B creates a board
    board_b_data = {
        "title": "User B's Board",
        "content": "Content by User B"
    }
    create_b_response = client.post(
        "/board",
        json=board_b_data,
        cookies={"session_id": session_b}
    )

    assert create_b_response.status_code == 201
    board_b = create_b_response.json()
    board_b_id = board_b["id"]
    assert board_b["user_id"] == user_b.id

    # When: 5. User A updates their own board (should succeed)
    update_a_data = {
        "title": "User A's Updated Board",
        "content": "Updated by User A"
    }
    update_a_response = client.patch(
        f"/board/{board_a_id}",
        json=update_a_data,
        cookies={"session_id": session_a}
    )

    # Then: User A can update their own board
    assert update_a_response.status_code == 200
    updated_board_a = update_a_response.json()
    assert updated_board_a["title"] == "User A's Updated Board"

    # When: 6. User A tries to update User B's board (should fail)
    update_b_attempt = {
        "title": "User A trying to hack",
        "content": "This should not work"
    }
    unauthorized_update_response = client.patch(
        f"/board/{board_b_id}",
        json=update_b_attempt,
        cookies={"session_id": session_a}
    )

    # Then: User A cannot update User B's board
    assert unauthorized_update_response.status_code == 403

    # When: 7. User B deletes their own board (should succeed)
    delete_b_response = client.delete(
        f"/board/{board_b_id}",
        cookies={"session_id": session_b}
    )

    # Then: User B can delete their own board
    assert delete_b_response.status_code == 204

    # When: 8. User B tries to delete User A's board (should fail)
    unauthorized_delete_response = client.delete(
        f"/board/{board_a_id}",
        cookies={"session_id": session_b}
    )

    # Then: User B cannot delete User A's board
    assert unauthorized_delete_response.status_code == 403

    # Final verification: User A's board still exists and is updated
    final_check_response = client.get(
        f"/board/{board_a_id}",
        cookies={"session_id": session_a}
    )

    assert final_check_response.status_code == 200
    final_board_a = final_check_response.json()
    assert final_board_a["title"] == "User A's Updated Board"
    assert final_board_a["user_id"] == user_a.id

    # User B's board should be deleted
    board_repository = BoardRepositoryImpl(db_session)
    deleted_board_b = board_repository.find_by_id(board_b_id)
    assert deleted_board_b is None