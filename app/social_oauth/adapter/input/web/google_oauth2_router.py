import uuid
from fastapi import APIRouter, Response, Request, Cookie
from fastapi.responses import RedirectResponse

from config.redis_config import get_redis
from app.social_oauth.application.usecase.google_oauth2_usecase import GoogleOAuth2UseCase
from app.social_oauth.infrastructure.service.google_oauth2_service import GoogleOAuth2Service

authentication_router = APIRouter()
service = GoogleOAuth2Service()
usecase = GoogleOAuth2UseCase(service)
redis_client = get_redis()


@authentication_router.get("/google")
async def redirect_to_google():
    url = usecase.get_authorization_url()
    print("[DEBUG] Redirecting to Google:", url)
    return RedirectResponse(url)


@authentication_router.get("/google/redirect")
async def process_google_redirect(
    response: Response,
    code: str,
    state: str | None = None
):
    print("[DEBUG] /google/redirect called")
    print("code:", code)
    print("state:", state)

    # code -> access token
    access_token = usecase.login_and_fetch_user(state or "", code)
    print("[DEBUG] Access token received:", access_token.access_token)

    # session_id 생성
    session_id = str(uuid.uuid4())
    print("[DEBUG] Generated session_id:", session_id)

    # Redis에 session 저장 (1시간 TTL)
    redis_client.set(session_id, access_token.access_token, ex=3600)
    print("[DEBUG] Session saved in Redis:", redis_client.exists(session_id))

    # 브라우저 쿠키 발급
    redirect_response = RedirectResponse("http://localhost:3000")
    redirect_response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=False,
        samesite="none",
        max_age=3600
    )
    print("[DEBUG] Cookie set in RedirectResponse directly")
    return redirect_response

@authentication_router.get("/status")
async def auth_status(request: Request, session_id: str | None = Cookie(None)):
    print("[DEBUG] /status called")

    # 모든 요청 헤더 출력
    print("[DEBUG] Request headers:", request.headers)

    # 쿠키 확인
    print("[DEBUG] Received session_id cookie:", session_id)

    if not session_id:
        print("[DEBUG] No session_id received. Returning logged_in: False")
        return {"logged_in": False}

    exists = redis_client.exists(session_id)
    print("[DEBUG] Redis has session_id?", exists)

    return {"logged_in": bool(exists)}
