import pytest
from unittest.mock import Mock

from app.board.application.use_case.get_board_detail import GetBoardDetail
from app.board.domain.board import Board
from app.board.domain.exceptions import BoardNotFoundException
from app.user.domain.user import User


def test_get_board_detail_authenticated():
    """인증된 사용자가 게시글 상세 조회"""
    # Given: Mock repositories
    mock_board_repository = Mock()
    mock_user_repository = Mock()

    board = Board(id=1, user_id=1, title="Test Board", content="Test Content")
    mock_board_repository.find_by_id.return_value = board

    author = User(google_id="g1", email="author@test.com", name="Author", profile_picture="pic.jpg")
    author.id = 1
    mock_user_repository.find_by_id.return_value = author

    use_case = GetBoardDetail(mock_board_repository, mock_user_repository)

    # When: 게시글 상세 조회
    result = use_case.execute(board_id=1)

    # Then: 게시글 정보가 반환됨
    assert result["id"] == 1
    assert result["title"] == "Test Board"
    assert result["content"] == "Test Content"
    assert result["user_id"] == 1
    mock_board_repository.find_by_id.assert_called_once_with(1)


def test_get_board_detail_not_found():
    """존재하지 않는 게시글 조회 시 예외 발생"""
    # Given: Mock repositories
    mock_board_repository = Mock()
    mock_user_repository = Mock()
    mock_board_repository.find_by_id.return_value = None

    use_case = GetBoardDetail(mock_board_repository, mock_user_repository)

    # When & Then: 존재하지 않는 게시글 조회 시 예외 발생
    with pytest.raises(BoardNotFoundException) as exc_info:
        use_case.execute(board_id=999)

    assert "999" in str(exc_info.value)


def test_board_response_includes_author_info():
    """Board 응답에 작성자 정보(name, profile_picture) 포함"""
    # Given: Mock repositories
    mock_board_repository = Mock()
    mock_user_repository = Mock()

    board = Board(id=1, user_id=1, title="Test Board", content="Test Content")
    mock_board_repository.find_by_id.return_value = board

    author = User(
        google_id="google_123",
        email="author@test.com",
        name="Test Author",
        profile_picture="https://example.com/pic.jpg"
    )
    author.id = 1
    mock_user_repository.find_by_id.return_value = author

    use_case = GetBoardDetail(mock_board_repository, mock_user_repository)

    # When: 게시글 상세 조회
    result = use_case.execute(board_id=1)

    # Then: 작성자 정보가 포함됨
    assert "author" in result
    assert result["author"]["id"] == 1
    assert result["author"]["name"] == "Test Author"
    assert result["author"]["email"] == "author@test.com"
    assert result["author"]["profile_picture"] == "https://example.com/pic.jpg"
    mock_user_repository.find_by_id.assert_called_once_with(1)