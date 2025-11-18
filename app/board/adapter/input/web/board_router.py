from typing import List

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.database.session import get_db
from app.board.application.use_case.create_board import CreateBoard
from app.board.application.use_case.get_board_list import GetBoardList
from app.board.infrastructure.repository.board_repository_impl import BoardRepositoryImpl
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl


board_router = APIRouter()


class CreateBoardRequest(BaseModel):
    title: str = Field(..., max_length=255)
    content: str = Field(..., max_length=2000)


class BoardResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: str
    updated_at: str


class AuthorResponse(BaseModel):
    id: int
    email: str
    name: str
    profile_picture: str


class BoardListItemResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    created_at: str
    updated_at: str
    author: AuthorResponse


@board_router.post("", status_code=status.HTTP_201_CREATED, response_model=BoardResponse)
async def create_board(
    request: CreateBoardRequest,
    x_user_id: int | None = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    """게시글 생성"""
    # 인증 확인
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Use Case 실행
    repository = BoardRepositoryImpl(db)
    use_case = CreateBoard(repository)

    try:
        board = use_case.execute(
            user_id=x_user_id,
            title=request.title,
            content=request.content
        )

        return BoardResponse(
            id=board.id,
            user_id=board.user_id,
            title=board.title,
            content=board.content,
            created_at=board.created_at.isoformat(),
            updated_at=board.updated_at.isoformat()
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@board_router.get("", response_model=List[BoardListItemResponse])
async def get_board_list(
    x_user_id: int | None = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db)
):
    """게시글 목록 조회"""
    # 인증 확인
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Use Case 실행
    board_repository = BoardRepositoryImpl(db)
    user_repository = UserRepositoryImpl(db)
    use_case = GetBoardList(board_repository, user_repository)

    try:
        board_list = use_case.execute(user_id=x_user_id)

        # Dict를 Response 모델로 변환
        return [
            BoardListItemResponse(
                id=board["id"],
                user_id=board["user_id"],
                title=board["title"],
                content=board["content"],
                created_at=board["created_at"].isoformat(),
                updated_at=board["updated_at"].isoformat(),
                author=AuthorResponse(
                    id=board["author"]["id"],
                    email=board["author"]["email"],
                    name=board["author"]["name"],
                    profile_picture=board["author"]["profile_picture"]
                )
            )
            for board in board_list
        ]
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
