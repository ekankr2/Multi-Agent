from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserResponse(BaseModel):
    """사용자 정보 응답 모델"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    profile_picture: str
    created_at: datetime
    updated_at: datetime
