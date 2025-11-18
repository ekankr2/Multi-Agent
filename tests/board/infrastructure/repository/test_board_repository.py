import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.database.session import Base
from app.user.infrastructure.orm.user_orm import UserORM  # noqa: F401 - Required for FK relationship
from app.board.infrastructure.orm.board_orm import BoardORM  # noqa: F401
from app.board.domain.board import Board
from app.board.infrastructure.repository.board_repository_impl import BoardRepositoryImpl


@pytest.fixture
def db_session():
    """테스트용 SQLite 데이터베이스 세션"""
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

    # Clean up test database file
    import os
    if os.path.exists("./test.db"):
        os.remove("./test.db")


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