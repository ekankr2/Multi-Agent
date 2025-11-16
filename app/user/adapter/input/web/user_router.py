from fastapi import APIRouter, Depends

from app.user.domain.user import User
from app.user.adapter.input.web.dependencies import get_current_user
from app.user.adapter.input.web.response.user_response import UserResponse


user_router = APIRouter()


@user_router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
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