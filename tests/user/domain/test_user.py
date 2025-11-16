import pytest
from datetime import datetime
import time


def test_user_creation_with_google_info():
    """User 엔티티 생성 시 Google 정보(google_id, email, name, profile_picture) 저장"""
    from app.user.domain.user import User

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


def test_user_has_timestamps():
    """User 엔티티 생성 시 created_at, updated_at, last_login_at 자동 설정"""
    from app.user.domain.user import User

    before_creation = datetime.now()
    user = User(
        google_id="123456789",
        email="test@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )
    after_creation = datetime.now()

    assert user.created_at is not None
    assert user.updated_at is not None
    assert user.last_login_at is not None

    assert before_creation <= user.created_at <= after_creation
    assert before_creation <= user.updated_at <= after_creation
    assert before_creation <= user.last_login_at <= after_creation


def test_user_update_name():
    """User 이름 업데이트 시 updated_at 갱신"""
    from app.user.domain.user import User

    user = User(
        google_id="123456789",
        email="test@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )

    original_updated_at = user.updated_at

    # Sleep to ensure time difference
    time.sleep(0.01)

    user.update_name("Updated User")

    assert user.name == "Updated User"
    assert user.updated_at > original_updated_at


def test_user_update_last_login():
    """로그인 시 last_login_at 갱신"""
    from app.user.domain.user import User

    user = User(
        google_id="123456789",
        email="test@example.com",
        name="Test User",
        profile_picture="https://example.com/photo.jpg"
    )

    original_last_login_at = user.last_login_at

    # Sleep to ensure time difference
    time.sleep(0.01)

    user.update_last_login()

    assert user.last_login_at > original_last_login_at