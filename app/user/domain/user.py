from datetime import datetime
from typing import Optional


class User:
    def __init__(self, google_id: str, email: str, name: str, profile_picture: str):
        self.id: Optional[int] = None
        self.google_id = google_id
        self.email = email
        self.name = name
        self.profile_picture = profile_picture

        now = datetime.now()
        self.created_at = now
        self.updated_at = now
        self.last_login_at = now

    def update_name(self, name: str):
        self.name = name
        self.updated_at = datetime.now()

    def update_last_login(self):
        self.last_login_at = datetime.now()
