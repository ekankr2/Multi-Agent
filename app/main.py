import os
from dotenv import load_dotenv

from anonymous_board.adapter.input.web.anonymous_board_router import anonymous_board_router
from board.adapter.input.web.board_router import board_router
from cart.adapter.input.web.cart_router import cart_router
from config.database.session import Base, engine
# from documents.adapter.input.web.documents_router import documents_router
from documents_openai.adapter.input.web.documents_openai_router import documents_openai_router

# from documents_multi_agents.adapter.input.web.document_multi_agent_router import documents_multi_agents_router
from financial_news.adapter.input.web.financial_news_router import financial_news_router
from kakao_authentication.adapter.input.web.kakao_authentication_router import kakao_authentication_router
from market_data.adapter.input.web.market_data_router import market_data_router
from mbti_analysis.adapter.input.web.mbti_analysis_router import mbti_analysis_router
from social_oauth.adapter.input.web.google_oauth2_router import authentication_router

# from financial_news.infrastructure.orm.models import Base

load_dotenv()

# os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
# os.environ["TORCH_USE_CUDA_DSA"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

frontend_url = os.getenv("CORS_ALLOWED_FRONTEND_URL")
origins = [frontend_url]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 정확한 origin만 허용
    allow_credentials=True,      # 쿠키 허용
    allow_methods=["*"],         # 모든 HTTP 메서드 허용
    allow_headers=["*"],         # 모든 헤더 허용
)

app.include_router(anonymous_board_router, prefix="/anonymouse-board")
app.include_router(authentication_router, prefix="/authentication")
app.include_router(board_router, prefix="/board")
# app.include_router(documents_router, prefix="/documents")
# app.include_router(documents_multi_agents_router, prefix="/documents-multi-agents")
app.include_router(documents_openai_router, prefix="/documents-openai")
app.include_router(market_data_router, prefix="/market-data")
app.include_router(cart_router, prefix="/cart")
app.include_router(financial_news_router, prefix="/financial-news")
app.include_router(kakao_authentication_router, prefix="/kakao-authentication")
app.include_router(mbti_analysis_router, prefix="/mbti-analysis")

# 앱 실행
if __name__ == "__main__":
    import uvicorn
    host = os.getenv("APP_HOST")
    port = int(os.getenv("APP_PORT"))
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host=host, port=port)
