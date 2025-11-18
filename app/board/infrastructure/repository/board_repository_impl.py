from sqlalchemy.orm import Session

from app.board.application.port.board_repository import BoardRepository
from app.board.domain.board import Board
from app.board.infrastructure.orm.board_orm import BoardORM


class BoardRepositoryImpl(BoardRepository):
    """게시판 리포지토리 구현"""

    def __init__(self, db: Session):
        self.db = db

    def save(self, board: Board) -> Board:
        """Board를 데이터베이스에 저장"""
        board_orm = BoardORM(
            user_id=board.user_id,
            title=board.title,
            content=board.content,
            created_at=board.created_at,
            updated_at=board.updated_at
        )

        self.db.add(board_orm)
        self.db.commit()
        self.db.refresh(board_orm)

        # ORM -> Domain Entity 변환
        return Board(
            id=board_orm.id,
            user_id=board_orm.user_id,
            title=board_orm.title,
            content=board_orm.content,
            created_at=board_orm.created_at,
            updated_at=board_orm.updated_at
        )