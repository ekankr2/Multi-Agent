from typing import Optional, Tuple
from fastapi import Header, HTTPException, Depends, Request
from sqlalchemy.orm import Session

from config.database.session import get_db
from config.redis_config import get_redis
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
    세션 쿠키에서 현재 인증된 사용자 조회

    세션 쿠키를 읽고 Redis에서 검증한 후 User 엔티티를 반환합니다.
    """
    # 1. 쿠키에서 session_id 추출
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="No session provided")

    # 2. Redis에서 세션 검증 및 user_id 조회
    redis_client = get_redis()
    user_id_str = redis_client.get(session_id)

    if not user_id_str:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    # 3. user_id로 User 조회
    user_id = int(user_id_str)
    repository = UserRepositoryImpl(db)
    user = repository.find_by_id(user_id)

    # 4. User가 없으면 401 에러 (세션은 있지만 사용자가 삭제된 경우)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user