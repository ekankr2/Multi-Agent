import pytest
from fastapi.testclient import TestClient

from app.main import app
from config.database.session import get_db
from app.user.domain.user import User
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from app.board.domain.board import Board
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


def test_get_board_list_endpoint(client, db_session, test_user):
    """GET /board - 게시글 목록 조회 성공"""
    # Given: 테스트용 게시글 2개 생성
    board_repository = BoardRepositoryImpl(db_session)
    board1 = Board(user_id=test_user.id, title="Board 1", content="Content 1")
    board2 = Board(user_id=test_user.id, title="Board 2", content="Content 2")
    board_repository.save(board1)
    board_repository.save(board2)

    # When: GET /board 요청 (인증된 사용자로)
    response = client.get(
        "/board",
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 게시글 목록이 반환됨
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    # 최신순 정렬 확인
    assert data[0]["title"] == "Board 2"
    assert data[1]["title"] == "Board 1"
    # 작성자 정보 포함 확인
    assert "author" in data[0]
    assert data[0]["author"]["name"] == test_user.name
    assert data[0]["author"]["profile_picture"] == test_user.profile_picture


def test_get_board_list_endpoint_unauthenticated(client):
    """GET /board - 인증 안 된 요청 시 401 에러"""
    # When: GET /board 요청 (인증 헤더 없이)
    response = client.get("/board")

    # Then: 401 Unauthorized 에러 반환
    assert response.status_code == 401


def test_get_board_detail_endpoint(client, db_session, test_user):
    """GET /board/{board_id} - 게시글 상세 조회 성공"""
    # Given: 테스트용 게시글 1개 생성
    board_repository = BoardRepositoryImpl(db_session)
    board = Board(user_id=test_user.id, title="Detail Board", content="Detail Content")
    saved_board = board_repository.save(board)

    # When: GET /board/{board_id} 요청 (인증된 사용자로)
    response = client.get(
        f"/board/{saved_board.id}",
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 게시글 상세 정보가 반환됨
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == saved_board.id
    assert data["title"] == "Detail Board"
    assert data["content"] == "Detail Content"
    assert data["user_id"] == test_user.id
    # 작성자 정보 포함 확인
    assert "author" in data
    assert data["author"]["name"] == test_user.name
    assert data["author"]["profile_picture"] == test_user.profile_picture


def test_get_board_detail_endpoint_not_found(client, test_user):
    """GET /board/{board_id} - 없는 게시글 조회 시 404 에러"""
    # When: GET /board/999 요청 (존재하지 않는 ID)
    response = client.get(
        "/board/999",
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 404 Not Found 에러 반환
    assert response.status_code == 404


def test_update_board_endpoint(client, db_session, test_user):
    """PATCH /board/{board_id} - 게시글 수정 성공"""
    # Given: 테스트용 게시글 1개 생성
    board_repository = BoardRepositoryImpl(db_session)
    board = Board(user_id=test_user.id, title="Original Title", content="Original Content")
    saved_board = board_repository.save(board)

    # When: PATCH /board/{board_id} 요청 (작성자로)
    update_data = {
        "title": "Updated Title",
        "content": "Updated Content"
    }
    response = client.patch(
        f"/board/{saved_board.id}",
        json=update_data,
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 게시글이 성공적으로 수정됨
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == saved_board.id
    assert data["title"] == "Updated Title"
    assert data["content"] == "Updated Content"
    assert data["user_id"] == test_user.id

    # 데이터베이스에서 확인
    updated_board = board_repository.find_by_id(saved_board.id)
    assert updated_board.title == "Updated Title"
    assert updated_board.content == "Updated Content"


def test_update_board_endpoint_forbidden(client, db_session, test_user):
    """PATCH /board/{board_id} - 작성자 아닌 경우 403 에러"""
    # Given: 다른 사용자가 작성한 게시글
    board_repository = BoardRepositoryImpl(db_session)
    other_user_id = test_user.id + 1  # 다른 사용자
    board = Board(user_id=other_user_id, title="Original Title", content="Original Content")
    saved_board = board_repository.save(board)

    # When: PATCH /board/{board_id} 요청 (다른 사용자로)
    update_data = {
        "title": "Updated Title",
        "content": "Updated Content"
    }
    response = client.patch(
        f"/board/{saved_board.id}",
        json=update_data,
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 403 Forbidden 에러 반환
    assert response.status_code == 403

    # 데이터베이스에서 확인 - 변경되지 않음
    unchanged_board = board_repository.find_by_id(saved_board.id)
    assert unchanged_board.title == "Original Title"
    assert unchanged_board.content == "Original Content"


def test_delete_board_endpoint(client, db_session, test_user):
    """DELETE /board/{board_id} - 게시글 삭제 성공"""
    # Given: 테스트용 게시글 1개 생성
    board_repository = BoardRepositoryImpl(db_session)
    board = Board(user_id=test_user.id, title="Test Board", content="Test Content")
    saved_board = board_repository.save(board)
    board_id = saved_board.id

    # When: DELETE /board/{board_id} 요청 (작성자로)
    response = client.delete(
        f"/board/{board_id}",
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 게시글이 성공적으로 삭제됨
    assert response.status_code == 204

    # 데이터베이스에서 확인 - 삭제됨
    deleted_board = board_repository.find_by_id(board_id)
    assert deleted_board is None


def test_delete_board_endpoint_forbidden(client, db_session, test_user):
    """DELETE /board/{board_id} - 작성자 아닌 경우 403 에러"""
    # Given: 다른 사용자가 작성한 게시글
    board_repository = BoardRepositoryImpl(db_session)
    other_user_id = test_user.id + 1  # 다른 사용자
    board = Board(user_id=other_user_id, title="Test Board", content="Test Content")
    saved_board = board_repository.save(board)
    board_id = saved_board.id

    # When: DELETE /board/{board_id} 요청 (다른 사용자로)
    response = client.delete(
        f"/board/{board_id}",
        headers={"X-User-Id": str(test_user.id)}
    )

    # Then: 403 Forbidden 에러 반환
    assert response.status_code == 403

    # 데이터베이스에서 확인 - 삭제되지 않음
    unchanged_board = board_repository.find_by_id(board_id)
    assert unchanged_board is not None
    assert unchanged_board.title == "Test Board"
