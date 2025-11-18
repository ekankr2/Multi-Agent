class BoardNotFoundException(Exception):
    """게시글을 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, board_id: int):
        self.board_id = board_id
        super().__init__(f"Board with id {board_id} not found")


class ForbiddenException(Exception):
    """권한이 없을 때 발생하는 예외"""

    def __init__(self, message: str = "You are not authorized to perform this action"):
        self.message = message
        super().__init__(message)