"""
Centralized router configuration.
All application routers are registered here and imported into main.py.
"""
from fastapi import FastAPI

from app.anonymous_board.adapter.input.web.anonymous_board_router import anonymous_board_router
from app.social_oauth.adapter.input.web.google_oauth2_router import authentication_router
from app.user.adapter.input.web.user_router import user_router
from app.board.adapter.input.web.board_router import board_router

# Import ORM models to register them with SQLAlchemy Base
from app.user.infrastructure.orm.user_orm import UserORM  # noqa: F401
from app.board.infrastructure.orm.board_orm import BoardORM  # noqa: F401


def setup_routers(app: FastAPI) -> None:
    """
    Register all application routers with the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # app.include_router(anonymous_board_router, prefix="/board")  # Replaced with board_router
    app.include_router(board_router, prefix="/board")
    app.include_router(authentication_router, prefix="/authentication")
    app.include_router(user_router, prefix="/user")