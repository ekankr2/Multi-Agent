class UserNotFoundException(Exception):
    """사용자를 찾을 수 없을 때 발생하는 예외"""

    def __init__(self, user_id: int):
        self.user_id = user_id
        super().__init__(f"User with id {user_id} not found")