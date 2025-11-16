from app.social_oauth.infrastructure.service.google_oauth2_service import GoogleOAuth2Service, GetAccessTokenRequest, \
    AccessToken


class GoogleOAuth2UseCase:
    def __init__(self, service: GoogleOAuth2Service):
        self.service = service

    def get_authorization_url(self) -> str:
        return self.service.get_authorization_url()

    def login_and_fetch_user(self, state: str, code: str) -> AccessToken:
        token_request = GetAccessTokenRequest(state=state, code=code)
        access_token = self.service.refresh_access_token(token_request)
        user_profile = self.service.fetch_user_profile(access_token)
        # 현재는 사용자 DB 처리 없이 반환만
        return access_token
