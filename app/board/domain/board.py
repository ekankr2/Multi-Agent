class Board:
    """게시판 엔티티"""

    def __init__(
        self,
        user_id: int,
        title: str,
        content: str,
        id: int | None = None
    ):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.content = content
