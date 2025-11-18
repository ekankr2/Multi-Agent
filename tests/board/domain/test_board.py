import pytest
from datetime import datetime


def test_board_creation_with_user_id():
    """Board 엔티티 생성 시 user_id 포함"""
    from app.board.domain.board import Board

    # Given: 사용자 ID와 게시글 정보
    user_id = 1
    title = "Test Board Title"
    content = "Test board content"

    # When: Board 엔티티 생성
    board = Board(
        user_id=user_id,
        title=title,
        content=content
    )

    # Then: Board 엔티티가 user_id를 포함
    assert board.user_id == user_id
    assert board.title == title
    assert board.content == content
