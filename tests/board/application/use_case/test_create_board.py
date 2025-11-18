import pytest
from unittest.mock import Mock

from app.board.application.use_case.create_board import CreateBoard
from app.board.domain.board import Board


def test_create_board_authenticated():
    """인증된 사용자가 게시글 작성"""
    # Given: Mock repository
    mock_repository = Mock()
    saved_board = Board(user_id=1, title="Test", content="Content", id=1)
    mock_repository.save.return_value = saved_board

    use_case = CreateBoard(mock_repository)

    # When: 게시글 생성
    result = use_case.execute(
        user_id=1,
        title="Test",
        content="Content"
    )

    # Then: 게시글이 생성됨
    assert result.id == 1
    assert result.user_id == 1
    assert result.title == "Test"
    assert result.content == "Content"
    mock_repository.save.assert_called_once()


def test_create_board_unauthenticated():
    """인증되지 않은 사용자는 게시글 작성 불가"""
    # Given: Mock repository
    mock_repository = Mock()
    use_case = CreateBoard(mock_repository)

    # When & Then: user_id가 None이면 예외 발생
    with pytest.raises(ValueError, match="User ID is required"):
        use_case.execute(
            user_id=None,
            title="Test",
            content="Content"
        )