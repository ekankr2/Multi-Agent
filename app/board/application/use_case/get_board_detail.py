from typing import Dict, Any

from app.board.application.port.board_repository import BoardRepository
from app.board.domain.exceptions import BoardNotFoundException
from app.user.application.port.user_repository_port import UserRepositoryPort


class GetBoardDetail:
    """게시글 상세 조회 유스케이스"""

    def __init__(self, board_repository: BoardRepository, user_repository: UserRepositoryPort):
        self.board_repository = board_repository
        self.user_repository = user_repository

    def execute(self, board_id: int) -> Dict[str, Any]:
        """게시글 상세 조회 (작성자 정보 포함)"""
        board = self.board_repository.find_by_id(board_id)

        if board is None:
            raise BoardNotFoundException(board_id)

        # 작성자 정보 조회
        author = self.user_repository.find_by_id(board.user_id)

        return {
            "id": board.id,
            "user_id": board.user_id,
            "title": board.title,
            "content": board.content,
            "created_at": board.created_at,
            "updated_at": board.updated_at,
            "author": {
                "id": author.id,
                "email": author.email,
                "name": author.name,
                "profile_picture": author.profile_picture
            }
        }