from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.domain.user import User


class RegisterOrLoginUser:
    def __init__(self, user_repository: UserRepositoryPort):
        self.user_repository = user_repository

    def execute(self, google_id: str, email: str, name: str, profile_picture: str) -> User:
        """
        Google 사용자 등록 또는 로그인
        - 새로운 사용자: 자동 회원가입
        - 기존 사용자: last_login_at 갱신
        """
        # 기존 사용자 확인
        existing_user = self.user_repository.find_by_google_id(google_id)

        if existing_user:
            # 기존 사용자: last_login_at 갱신
            existing_user.update_last_login()
            return self.user_repository.update(existing_user)
        else:
            # 새로운 사용자: 회원가입
            new_user = User(
                google_id=google_id,
                email=email,
                name=name,
                profile_picture=profile_picture
            )
            return self.user_repository.save(new_user)