from typing import List, Dict, Any

from app.board.application.port.board_repository import BoardRepository
from app.user.application.port.user_repository_port import UserRepositoryPort


class GetBoardList:
    """게시글 목록 조회 유스케이스"""

    def __init__(self, board_repository: BoardRepository, user_repository: UserRepositoryPort):
        self.board_repository = board_repository
        self.user_repository = user_repository

    def execute(self, user_id: int | None) -> List[Dict[str, Any]]:
        """게시글 목록 조회 (작성자 정보 포함)"""
        if user_id is None:
            raise ValueError("User ID is required")

        boards = self.board_repository.find_all()

        # 각 게시글에 작성자 정보 추가
        result = []
        for board in boards:
            author = self.user_repository.find_by_id(board.user_id)
            board_dict = {
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
            result.append(board_dict)

        return result