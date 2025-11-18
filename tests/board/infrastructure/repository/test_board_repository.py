from app.board.domain.board import Board
from app.board.infrastructure.repository.board_repository_impl import BoardRepositoryImpl


def test_board_repository_save(db_session):
    """BoardRepository가 Board를 데이터베이스에 저장"""
    # Given: Board 엔티티
    repository = BoardRepositoryImpl(db_session)
    board = Board(
        user_id=1,
        title="Test Board",
        content="Test Content"
    )

    # When: Board 저장
    saved_board = repository.save(board)

    # Then: Board가 저장되고 ID가 할당됨
    assert saved_board.id is not None
    assert saved_board.user_id == 1
    assert saved_board.title == "Test Board"
    assert saved_board.content == "Test Content"
    assert saved_board.created_at is not None
    assert saved_board.updated_at is not None