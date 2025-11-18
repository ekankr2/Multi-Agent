from datetime import datetime, UTC


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
        self.created_at = created_at or datetime.now(UTC)
        self.updated_at = updated_at or datetime.now(UTC)

    def update(self, title: str, content: str) -> None:
        """Board의 제목과 내용을 수정하고 updated_at을 갱신"""
        # Validation
        if len(title) > 255:
            raise ValueError("Title must be 255 characters or less")
        if len(content) > 2000:
            raise ValueError("Content must be 2000 characters or less")

        self.title = title
        self.content = content
        self.updated_at = datetime.now(UTC)
