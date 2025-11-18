from app.board.application.port.board_repository import BoardRepository
from app.board.domain.board import Board
from app.board.domain.exceptions import BoardNotFoundException, ForbiddenException
from app.user.application.port.user_repository_port import UserRepositoryPort


class UpdateBoard:
    """게시글 수정 유스케이스 (작성자 권한 검증 포함)"""

    def __init__(self, board_repository: BoardRepository, user_repository: UserRepositoryPort):
        self.board_repository = board_repository
        self.user_repository = user_repository

    def execute(self, board_id: int, user_id: int, title: str, content: str) -> Board:
        """게시글 수정 (작성자만 가능)"""
        # 게시글 조회
        board = self.board_repository.find_by_id(board_id)

        if board is None:
            raise BoardNotFoundException(board_id)

        # 작성자 권한 검증
        if board.user_id != user_id:
            raise ForbiddenException("You are not authorized to update this board")

        # 게시글 수정
        board.update(title=title, content=content)

        # 데이터베이스 업데이트
        return self.board_repository.update(board)