import pytest
from datetime import datetime


def test_user_creation_with_google_info():
    """User 엔티티 생성 시 Google 정보(google_id, email, name, profile_picture) 저장"""
    from user.domain.user import User

    google_id = "123456789"
    email = "test@example.com"
    name = "Test User"
    profile_picture = "https://example.com/photo.jpg"

    user = User(
        google_id=google_id,
        email=email,
        name=name,
        profile_picture=profile_picture
    )

    assert user.google_id == google_id
    assert user.email == email
    assert user.name == name
    assert user.profile_picture == profile_picture