from app.board.application.port.board_repository import BoardRepository
from app.board.domain.board import Board


class CreateBoard:
    """게시글 생성 유스케이스"""

    def __init__(self, board_repository: BoardRepository):
        self.board_repository = board_repository

    def execute(self, user_id: int | None, title: str, content: str) -> Board:
        """게시글 생성"""
        if user_id is None:
            raise ValueError("User ID is required")

        board = Board(
            user_id=user_id,
            title=title,
            content=content
        )

        return self.board_repository.save(board)