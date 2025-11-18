class BoardNotFoundException(Exception):
    """게시글을 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, board_id: int):
        self.board_id = board_id
        super().__init__(f"Board with id {board_id} not found")