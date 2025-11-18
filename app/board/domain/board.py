from datetime import datetime


class Board:
    """게시판 엔티티"""

    def __init__(
        self,
        user_id: int,
        title: str,
        content: str,
        id: int | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None
    ):
        # Validation
        if len(title) > 255:
            raise ValueError("Title must be 255 characters or less")
        if len(content) > 2000:
            raise ValueError("Content must be 2000 characters or less")

        self.id = id
        self.user_id = user_id
        self.title = title
        self.content = content
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
