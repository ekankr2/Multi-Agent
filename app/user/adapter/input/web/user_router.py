from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.user.domain.user import User
from app.user.adapter.input.web.dependencies import get_current_user_from_session
from app.user.adapter.input.web.response.user_response import UserResponse
from app.user.adapter.input.web.request.update_user_request import UpdateUserRequest
from app.user.application.use_case.update_user_profile import UpdateUserProfile
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from config.database.session import get_db


user_router = APIRouter()


@user_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user_from_session)):
    """
    GET /user/me - 인증된 사용자 정보 조회

    인증된 사용자의 정보를 반환합니다.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        profile_picture=current_user.profile_picture,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@user_router.patch("/me", response_model=UserResponse)
def patch_me(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    """
    PATCH /user/me - 사용자 정보 수정

    인증된 사용자의 프로필 정보를 수정합니다.
    """
    repository = UserRepositoryImpl(db)
    use_case = UpdateUserProfile(repository)

    updated_user = use_case.execute(current_user.id, request.name)

    return UserResponse(
        id=updated_user.id,
        email=updated_user.email,
        name=updated_user.name,
        profile_picture=updated_user.profile_picture,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )