from datetime import datetime


class User:
    def __init__(self, google_id: str, email: str, name: str, profile_picture: str):
        self.google_id = google_id
        self.email = email
        self.name = name
        self.profile_picture = profile_picture

        now = datetime.now()
        self.created_at = now
        self.updated_at = now
        self.last_login_at = now
