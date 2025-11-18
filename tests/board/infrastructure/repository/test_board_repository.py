import time

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


def test_board_repository_find_all(db_session):
    """전체 Board 목록 조회 (최신순 정렬)"""
    # Given: 3개의 Board를 시간 간격을 두고 저장
    repository = BoardRepositoryImpl(db_session)

    board1 = Board(user_id=1, title="First Board", content="Content 1")
    saved_board1 = repository.save(board1)
    time.sleep(0.01)  # 생성 시간 차이를 위한 대기

    board2 = Board(user_id=1, title="Second Board", content="Content 2")
    saved_board2 = repository.save(board2)
    time.sleep(0.01)

    board3 = Board(user_id=2, title="Third Board", content="Content 3")
    saved_board3 = repository.save(board3)

    # When: 전체 Board 목록 조회
    boards = repository.find_all()

    # Then: 모든 Board가 최신순으로 반환됨
    assert len(boards) == 3
    assert boards[0].id == saved_board3.id  # 가장 최근
    assert boards[1].id == saved_board2.id
    assert boards[2].id == saved_board1.id  # 가장 오래된