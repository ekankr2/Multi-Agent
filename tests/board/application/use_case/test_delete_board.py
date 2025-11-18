import pytest
from unittest.mock import Mock

from app.board.application.use_case.delete_board import DeleteBoard
from app.board.domain.board import Board
from app.board.domain.exceptions import BoardNotFoundException, ForbiddenException


def test_delete_board_by_author():
    """작성자가 본인 게시글 삭제 성공"""
    # Given: Mock repository
    mock_board_repository = Mock()

    board = Board(id=1, user_id=1, title="Test Board", content="Test Content")
    mock_board_repository.find_by_id.return_value = board

    use_case = DeleteBoard(mock_board_repository)

    # When: 작성자가 본인 게시글 삭제
    use_case.execute(board_id=1, user_id=1)

    # Then: 게시글이 삭제됨
    mock_board_repository.find_by_id.assert_called_once_with(1)
    mock_board_repository.delete.assert_called_once_with(1)


def test_delete_board_by_non_author():
    """다른 사용자가 삭제 시도 시 403 에러"""
    # Given: Mock repository
    mock_board_repository = Mock()

    board = Board(id=1, user_id=1, title="Test Board", content="Test Content")
    mock_board_repository.find_by_id.return_value = board

    use_case = DeleteBoard(mock_board_repository)

    # When & Then: 다른 사용자가 삭제 시도 시 예외 발생
    with pytest.raises(ForbiddenException) as exc_info:
        use_case.execute(board_id=1, user_id=2)  # 다른 사용자

    assert "You are not authorized to delete this board" in str(exc_info.value)
    mock_board_repository.find_by_id.assert_called_once_with(1)
    # delete는 호출되지 않아야 함
    mock_board_repository.delete.assert_not_called()