import pytest
from unittest.mock import Mock

from app.board.application.use_case.update_board import UpdateBoard
from app.board.domain.board import Board
from app.board.domain.exceptions import BoardNotFoundException, ForbiddenException


def test_update_board_by_author():
    """작성자가 본인 게시글 수정 성공"""
    # Given: Mock repositories
    mock_board_repository = Mock()
    mock_user_repository = Mock()

    board = Board(id=1, user_id=1, title="Original Title", content="Original Content")
    mock_board_repository.find_by_id.return_value = board
    mock_board_repository.update.return_value = board

    use_case = UpdateBoard(mock_board_repository, mock_user_repository)

    # When: 작성자가 본인 게시글 수정
    result = use_case.execute(
        board_id=1,
        user_id=1,
        title="Updated Title",
        content="Updated Content"
    )

    # Then: 게시글이 수정됨
    assert result.title == "Updated Title"
    assert result.content == "Updated Content"
    mock_board_repository.find_by_id.assert_called_once_with(1)
    mock_board_repository.update.assert_called_once()


def test_update_board_by_non_author():
    """다른 사용자가 수정 시도 시 403 에러"""
    # Given: Mock repositories
    mock_board_repository = Mock()
    mock_user_repository = Mock()

    board = Board(id=1, user_id=1, title="Original Title", content="Original Content")
    mock_board_repository.find_by_id.return_value = board

    use_case = UpdateBoard(mock_board_repository, mock_user_repository)

    # When & Then: 다른 사용자가 수정 시도 시 예외 발생
    with pytest.raises(ForbiddenException) as exc_info:
        use_case.execute(
            board_id=1,
            user_id=2,  # 다른 사용자
            title="Updated Title",
            content="Updated Content"
        )

    assert "You are not authorized to update this board" in str(exc_info.value)
    mock_board_repository.find_by_id.assert_called_once_with(1)
    # update는 호출되지 않아야 함
    mock_board_repository.update.assert_not_called()