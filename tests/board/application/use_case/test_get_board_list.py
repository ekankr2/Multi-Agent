import pytest
from unittest.mock import Mock

from app.board.application.use_case.get_board_list import GetBoardList
from app.board.domain.board import Board
from app.user.domain.user import User


def test_get_board_list_authenticated():
    """인증된 사용자가 게시글 목록 조회"""
    # Given: Mock repositories with boards
    mock_board_repository = Mock()
    mock_user_repository = Mock()

    board1 = Board(id=1, user_id=1, title="Board 1", content="Content 1")
    board2 = Board(id=2, user_id=2, title="Board 2", content="Content 2")
    mock_board_repository.find_all.return_value = [board1, board2]

    user1 = User(google_id="g1", email="user1@test.com", name="User 1", profile_picture="pic1.jpg")
    user1.id = 1
    user2 = User(google_id="g2", email="user2@test.com", name="User 2", profile_picture="pic2.jpg")
    user2.id = 2
    mock_user_repository.find_by_id.side_effect = lambda uid: user1 if uid == 1 else user2

    use_case = GetBoardList(mock_board_repository, mock_user_repository)

    # When: 게시글 목록 조회 (인증된 사용자)
    result = use_case.execute(user_id=1)

    # Then: 게시글 목록이 반환됨
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[0]["title"] == "Board 1"
    assert result[1]["id"] == 2
    assert result[1]["title"] == "Board 2"
    mock_board_repository.find_all.assert_called_once()


def test_get_board_list_unauthenticated():
    """인증되지 않은 사용자는 목록 조회 불가"""
    # Given: Mock repositories
    mock_board_repository = Mock()
    mock_user_repository = Mock()
    use_case = GetBoardList(mock_board_repository, mock_user_repository)

    # When & Then: user_id가 None이면 예외 발생
    with pytest.raises(ValueError, match="User ID is required"):
        use_case.execute(user_id=None)


def test_board_list_response_includes_author_info():
    """Board 목록 응답 각 항목에 작성자 정보 포함"""
    # Given: Mock repositories
    mock_board_repository = Mock()
    mock_user_repository = Mock()

    board = Board(id=1, user_id=1, title="Test Board", content="Content")
    mock_board_repository.find_all.return_value = [board]

    author = User(
        google_id="google_123",
        email="author@test.com",
        name="Test Author",
        profile_picture="https://example.com/pic.jpg"
    )
    author.id = 1
    mock_user_repository.find_by_id.return_value = author

    use_case = GetBoardList(mock_board_repository, mock_user_repository)

    # When: 게시글 목록 조회
    result = use_case.execute(user_id=1)

    # Then: 작성자 정보가 포함됨
    assert len(result) == 1
    assert result[0]["author"]["id"] == 1
    assert result[0]["author"]["name"] == "Test Author"
    assert result[0]["author"]["profile_picture"] == "https://example.com/pic.jpg"
    assert "email" in result[0]["author"]  # email도 포함
    mock_user_repository.find_by_id.assert_called_once_with(1)