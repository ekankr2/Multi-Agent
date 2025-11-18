from typing import Optional, Tuple
from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session

from config.database.session import get_db
from app.user.application.use_case.get_user_by_id import GetUserById
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from app.user.domain.user import User
from app.user.domain.exceptions import UserNotFoundException


def get_current_user(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db)
) -> User:
    """
    현재 인증된 사용자 조회 (임시 구현)

    TODO: Phase 3에서 session-based authentication으로 교체 예정
    """
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    repository = UserRepositoryImpl(db)
    use_case = GetUserById(repository)

    try:
        return use_case.execute(user_id)
    except UserNotFoundException:
        raise HTTPException(status_code=401, detail="Unauthorized")


def get_current_user_and_db(
    x_user_id: Optional[str] = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db)
) -> Tuple[User, Session]:
    """
    현재 인증된 사용자와 DB 세션을 함께 반환

    TODO: Phase 3에서 session-based authentication으로 교체 예정
    """
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user ID")

    repository = UserRepositoryImpl(db)
    use_case = GetUserById(repository)

    try:
        user = use_case.execute(user_id)
        return user, db
    except UserNotFoundException:
        raise HTTPException(status_code=401, detail="Unauthorized")