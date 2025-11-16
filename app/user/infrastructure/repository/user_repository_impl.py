from typing import Optional
from sqlalchemy.orm import Session

from app.user.application.port.user_repository_port import UserRepositoryPort
from app.user.domain.user import User
from app.user.infrastructure.orm.user_orm import UserORM


class UserRepositoryImpl(UserRepositoryPort):
    def __init__(self, db_session: Session):
        self.db = db_session

    def save(self, user: User) -> User:
        orm_user = UserORM(
            google_id=user.google_id,
            email=user.email,
            name=user.name,
            profile_picture=user.profile_picture,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login_at=user.last_login_at
        )
        self.db.add(orm_user)
        self.db.commit()
        self.db.refresh(orm_user)

        user.id = orm_user.id
        user.created_at = orm_user.created_at
        user.updated_at = orm_user.updated_at
        user.last_login_at = orm_user.last_login_at
        return user

    def find_by_google_id(self, google_id: str) -> Optional[User]:
        orm_user = self.db.query(UserORM).filter(UserORM.google_id == google_id).first()
        if orm_user:
            user = User(
                google_id=orm_user.google_id,
                email=orm_user.email,
                name=orm_user.name,
                profile_picture=orm_user.profile_picture
            )
            user.id = orm_user.id
            user.created_at = orm_user.created_at
            user.updated_at = orm_user.updated_at
            user.last_login_at = orm_user.last_login_at
            return user
        return None

    def find_by_id(self, user_id: int) -> Optional[User]:
        orm_user = self.db.query(UserORM).filter(UserORM.id == user_id).first()
        if orm_user:
            user = User(
                google_id=orm_user.google_id,
                email=orm_user.email,
                name=orm_user.name,
                profile_picture=orm_user.profile_picture
            )
            user.id = orm_user.id
            user.created_at = orm_user.created_at
            user.updated_at = orm_user.updated_at
            user.last_login_at = orm_user.last_login_at
            return user
        return None

    def update(self, user: User) -> User:
        orm_user = self.db.query(UserORM).filter(UserORM.id == user.id).first()
        if orm_user:
            orm_user.name = user.name
            orm_user.email = user.email
            orm_user.profile_picture = user.profile_picture
            orm_user.updated_at = user.updated_at
            orm_user.last_login_at = user.last_login_at

            self.db.commit()
            self.db.refresh(orm_user)

            user.updated_at = orm_user.updated_at
        return user
