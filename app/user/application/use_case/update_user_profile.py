from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.domain.user import User
from app.user.domain.exceptions import UserNotFoundException


class UpdateUserProfile:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, user_id: int, new_name: str) -> User:
        """
        사용자 프로필 업데이트 (이름 변경)
        """
        user = self.user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundException(user_id)

        user.update_name(new_name)
        return self.user_repository.update(user)
