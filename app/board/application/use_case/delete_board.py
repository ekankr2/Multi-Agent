from app.board.application.port.board_repository import BoardRepository
from app.board.domain.exceptions import BoardNotFoundException, ForbiddenException


class DeleteBoard:
    """게시글 삭제 유스케이스 (작성자 권한 검증 포함)"""

    def __init__(self, board_repository: BoardRepository):
        self.board_repository = board_repository

    def execute(self, board_id: int, user_id: int) -> None:
        """게시글 삭제 (작성자만 가능)"""
        # 게시글 조회
        board = self.board_repository.find_by_id(board_id)

        if board is None:
            raise BoardNotFoundException(board_id)

        # 작성자 권한 검증
        if board.user_id != user_id:
            raise ForbiddenException("You are not authorized to delete this board")

        # 게시글 삭제
        self.board_repository.delete(board_id)