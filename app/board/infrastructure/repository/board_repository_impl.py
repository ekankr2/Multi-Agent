from typing import List, Optional

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

    def find_all(self) -> List[Board]:
        """전체 Board 목록을 최신순으로 조회"""
        board_orms = self.db.query(BoardORM).order_by(BoardORM.created_at.desc()).all()

        # ORM -> Domain Entity 변환
        return [
            Board(
                id=board_orm.id,
                user_id=board_orm.user_id,
                title=board_orm.title,
                content=board_orm.content,
                created_at=board_orm.created_at,
                updated_at=board_orm.updated_at
            )
            for board_orm in board_orms
        ]

    def find_by_id(self, board_id: int) -> Optional[Board]:
        """id로 Board 조회"""
        board_orm = self.db.query(BoardORM).filter(BoardORM.id == board_id).first()

        if board_orm is None:
            return None

        # ORM -> Domain Entity 변환
        return Board(
            id=board_orm.id,
            user_id=board_orm.user_id,
            title=board_orm.title,
            content=board_orm.content,
            created_at=board_orm.created_at,
            updated_at=board_orm.updated_at
        )

    def update(self, board: Board) -> Board:
        """Board를 업데이트하고 업데이트된 Board 반환"""
        board_orm = self.db.query(BoardORM).filter(BoardORM.id == board.id).first()

        if board_orm is None:
            raise ValueError(f"Board with id {board.id} not found")

        # Domain Entity -> ORM 업데이트
        board_orm.title = board.title
        board_orm.content = board.content
        board_orm.updated_at = board.updated_at

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