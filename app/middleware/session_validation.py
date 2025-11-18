from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from redis import Redis


class SessionValidationMiddleware(BaseHTTPMiddleware):
    """세션 검증 미들웨어 - 쿠키의 session_id를 검증하고 user_id를 주입"""

    def __init__(self, app, redis_client: Redis):
        super().__init__(app)
        self.redis_client = redis_client

    async def dispatch(self, request: Request, call_next):
        # 쿠키에서 session_id 추출
        session_id = request.cookies.get("session_id")

        # 세션 쿠키가 없으면 401
        if not session_id:
            return JSONResponse(
                status_code=401,
                content={"detail": "No session provided"}
            )

        # Redis에서 세션 조회
        user_id_str = self.redis_client.get(session_id)

        # 세션이 없거나 만료되었으면 401
        if not user_id_str:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired session"}
            )

        # request.state에 user_id 주입
        request.state.user_id = int(user_id_str)

        # 다음 핸들러로 진행
        response = await call_next(request)
        return response
