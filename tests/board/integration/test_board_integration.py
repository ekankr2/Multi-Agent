"""
Board Domain Integration Tests

이 테스트들은 Board Domain의 전체 플로우를 검증합니다:
- Use Case Layer
- Repository Layer
- Domain Layer
- Web Adapter Layer
의 통합 동작을 확인합니다.
"""
import pytest
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


@pytest.fixture
def test_user(db_session):
    """테스트용 사용자 생성"""
    repository = UserRepositoryImpl(db_session)
    user = User(
        google_id="google_board_integration_123",
        email="board_integration@example.com",
        name="Board Integration User",
        profile_picture="https://example.com/board_integration.jpg"
    )
    return repository.save(user)


def test_board_full_workflow_single_user(client, test_user, create_session_cookie, db_session):
    """게시글 작성 → 조회 → 수정 → 삭제 전체 플로우"""
    # Given: 인증된 사용자의 세션 쿠키
    session_cookie = create_session_cookie(test_user.id)

    # When: 1. 게시글 작성 (POST /board)
    create_data = {
        "title": "Integration Test Board",
        "content": "This is an integration test board content"
    }
    create_response = client.post(
        "/board",
        json=create_data,
        cookies=session_cookie
    )

    # Then: 게시글이 성공적으로 생성됨
    assert create_response.status_code == 201
    created_board = create_response.json()
    assert created_board["title"] == "Integration Test Board"
    assert created_board["content"] == "This is an integration test board content"
    assert created_board["user_id"] == test_user.id
    board_id = created_board["id"]

    # When: 2. 게시글 목록 조회 (GET /board)
    list_response = client.get("/board", cookies=session_cookie)

    # Then: 작성한 게시글이 목록에 포함됨
    assert list_response.status_code == 200
    board_list = list_response.json()
    assert len(board_list) >= 1
    # 최신 게시글이 첫 번째에 있어야 함 (최신순 정렬)
    found_board = next((b for b in board_list if b["id"] == board_id), None)
    assert found_board is not None
    assert found_board["title"] == "Integration Test Board"
    assert "author" in found_board
    assert found_board["author"]["name"] == test_user.name

    # When: 3. 게시글 상세 조회 (GET /board/{id})
    detail_response = client.get(f"/board/{board_id}", cookies=session_cookie)

    # Then: 상세 정보가 정상적으로 조회됨
    assert detail_response.status_code == 200
    board_detail = detail_response.json()
    assert board_detail["id"] == board_id
    assert board_detail["title"] == "Integration Test Board"
    assert board_detail["content"] == "This is an integration test board content"
    assert board_detail["user_id"] == test_user.id
    assert "author" in board_detail
    assert board_detail["author"]["name"] == test_user.name

    # When: 4. 게시글 수정 (PATCH /board/{id})
    update_data = {
        "title": "Updated Integration Test Board",
        "content": "Updated content for integration test"
    }
    update_response = client.patch(
        f"/board/{board_id}",
        json=update_data,
        cookies=session_cookie
    )

    # Then: 게시글이 성공적으로 수정됨
    assert update_response.status_code == 200
    updated_board = update_response.json()
    assert updated_board["id"] == board_id
    assert updated_board["title"] == "Updated Integration Test Board"
    assert updated_board["content"] == "Updated content for integration test"
    assert updated_board["user_id"] == test_user.id

    # When: 5. 수정된 게시글 재조회
    updated_detail_response = client.get(f"/board/{board_id}", cookies=session_cookie)

    # Then: 수정사항이 반영되어 있음
    assert updated_detail_response.status_code == 200
    final_board = updated_detail_response.json()
    assert final_board["title"] == "Updated Integration Test Board"
    assert final_board["content"] == "Updated content for integration test"

    # When: 6. 게시글 삭제 (DELETE /board/{id})
    delete_response = client.delete(f"/board/{board_id}", cookies=session_cookie)

    # Then: 게시글이 성공적으로 삭제됨
    assert delete_response.status_code == 204

    # When: 7. 삭제 후 조회 시도
    deleted_response = client.get(f"/board/{board_id}", cookies=session_cookie)

    # Then: 404 에러 반환
    assert deleted_response.status_code == 404


def test_board_authorization_workflow(client, db_session, create_session_cookie):
    """사용자 A가 작성, 사용자 B가 수정/삭제 시도 시 403 에러"""
    # Given: 두 명의 사용자 생성
    repository = UserRepositoryImpl(db_session)

    user_a = User(
        google_id="google_user_a_123",
        email="user_a@example.com",
        name="User A",
        profile_picture="https://example.com/user_a.jpg"
    )
    user_a = repository.save(user_a)

    user_b = User(
        google_id="google_user_b_456",
        email="user_b@example.com",
        name="User B",
        profile_picture="https://example.com/user_b.jpg"
    )
    user_b = repository.save(user_b)

    # Given: 사용자 A의 세션 쿠키
    session_a = create_session_cookie(user_a.id, session_id="session-a")

    # When: 1. 사용자 A가 게시글 작성
    create_data = {
        "title": "User A's Board",
        "content": "This board belongs to User A"
    }
    create_response = client.post(
        "/board",
        json=create_data,
        cookies=session_a
    )

    # Then: 게시글이 성공적으로 생성됨
    assert create_response.status_code == 201
    board = create_response.json()
    assert board["user_id"] == user_a.id
    board_id = board["id"]

    # Given: 사용자 B의 세션 쿠키
    session_b = create_session_cookie(user_b.id, session_id="session-b")

    # When: 2. 사용자 B가 사용자 A의 게시글 수정 시도
    update_data = {
        "title": "User B trying to modify",
        "content": "User B's attempt to modify"
    }
    update_response = client.patch(
        f"/board/{board_id}",
        json=update_data,
        cookies=session_b
    )

    # Then: 403 Forbidden 에러 반환
    assert update_response.status_code == 403

    # When: 3. 사용자 B가 사용자 A의 게시글 삭제 시도
    delete_response = client.delete(f"/board/{board_id}", cookies=session_b)

    # Then: 403 Forbidden 에러 반환
    assert delete_response.status_code == 403

    # When: 4. 사용자 A로 다시 전환하여 게시글 확인
    detail_response = client.get(f"/board/{board_id}", cookies=session_a)

    # Then: 게시글이 변경되지 않았음을 확인
    assert detail_response.status_code == 200
    unchanged_board = detail_response.json()
    assert unchanged_board["title"] == "User A's Board"
    assert unchanged_board["content"] == "This board belongs to User A"
    assert unchanged_board["user_id"] == user_a.id

    # Cleanup: 사용자 A가 자신의 게시글 삭제
    cleanup_response = client.delete(f"/board/{board_id}", cookies=session_a)
    assert cleanup_response.status_code == 204