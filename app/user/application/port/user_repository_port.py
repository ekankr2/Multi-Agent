from abc import ABC, abstractmethod
from typing import Optional

from app.user.domain.user import User


class UserRepositoryPort(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_google_id(self, google_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass
