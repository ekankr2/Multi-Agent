from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.domain.user import User


class GetUserById:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, user_id: int) -> User:
        """
        ID로 사용자 조회
        """
        return self.user_repository.find_by_id(user_id)