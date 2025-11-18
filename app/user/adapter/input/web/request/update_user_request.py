from pydantic import BaseModel


class UpdateUserRequest(BaseModel):
    """사용자 프로필 업데이트 요청"""
    name: str