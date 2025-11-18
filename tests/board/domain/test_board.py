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


def test_board_has_title_and_content():
    """Board는 title(최대 255자), content(최대 2000자) 포함"""
    from app.board.domain.board import Board

    # Given: 최대 길이의 제목과 내용
    title = "A" * 255
    content = "B" * 2000

    # When: Board 엔티티 생성
    board = Board(
        user_id=1,
        title=title,
        content=content
    )

    # Then: 제목과 내용이 정상적으로 저장됨
    assert board.title == title
    assert len(board.title) == 255
    assert board.content == content
    assert len(board.content) == 2000


def test_board_has_timestamps():
    """Board 생성 시 created_at, updated_at 자동 설정"""
    from app.board.domain.board import Board

    # When: Board 엔티티 생성
    board = Board(
        user_id=1,
        title="Test Title",
        content="Test Content"
    )

    # Then: 타임스탬프가 자동으로 설정됨
    assert board.created_at is not None
    assert board.updated_at is not None
    assert isinstance(board.created_at, datetime)
    assert isinstance(board.updated_at, datetime)


def test_board_title_max_length_validation():
    """title이 255자 초과 시 예외 발생"""
    from app.board.domain.board import Board

    # Given: 256자 제목
    title = "A" * 256

    # When & Then: 예외 발생
    with pytest.raises(ValueError, match="Title must be 255 characters or less"):
        Board(
            user_id=1,
            title=title,
            content="Test Content"
        )


def test_board_content_max_length_validation():
    """content가 2000자 초과 시 예외 발생"""
    from app.board.domain.board import Board

    # Given: 2001자 내용
    content = "A" * 2001

    # When & Then: 예외 발생
    with pytest.raises(ValueError, match="Content must be 2000 characters or less"):
        Board(
            user_id=1,
            title="Test Title",
            content=content
        )
