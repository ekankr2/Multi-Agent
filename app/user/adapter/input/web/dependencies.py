from typing import Optional, Tuple
from fastapi import Header, HTTPException, Depends, Request
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


def get_current_user_from_session(
    request: Request,
    db: Session = Depends(get_db)
) -> User:
    """
    세션에서 현재 인증된 사용자 조회

    SessionValidationMiddleware가 request.state.user_id를 주입한 후 호출됨.
    """
    # request.state에서 user_id 추출 (SessionValidationMiddleware가 주입)
    user_id = request.state.user_id

    # UserRepository로 User 조회
    repository = UserRepositoryImpl(db)
    user = repository.find_by_id(user_id)

    # User가 없으면 401 에러 (세션은 있지만 사용자가 삭제된 경우)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user