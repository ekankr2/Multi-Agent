from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.database.session import get_db
from app.board.application.use_case.create_board import CreateBoard
from app.board.application.use_case.get_board_list import GetBoardList
from app.board.application.use_case.get_board_detail import GetBoardDetail
from app.board.application.use_case.update_board import UpdateBoard
from app.board.application.use_case.delete_board import DeleteBoard
from app.board.domain.exceptions import BoardNotFoundException, ForbiddenException
from app.board.infrastructure.repository.board_repository_impl import BoardRepositoryImpl
from app.user.infrastructure.repository.user_repository_impl import UserRepositoryImpl
from app.user.adapter.input.web.dependencies import get_current_user_from_session
from app.user.domain.user import User


board_router = APIRouter()


class CreateBoardRequest(BaseModel):
    title: str = Field(..., max_length=255)
    content: str = Field(..., max_length=2000)


class UpdateBoardRequest(BaseModel):
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
    current_user: User = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    """게시글 생성"""
    # Use Case 실행
    repository = BoardRepositoryImpl(db)
    use_case = CreateBoard(repository)

    try:
        board = use_case.execute(
            user_id=current_user.id,
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
    current_user: User = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    """게시글 목록 조회"""
    # Use Case 실행
    board_repository = BoardRepositoryImpl(db)
    user_repository = UserRepositoryImpl(db)
    use_case = GetBoardList(board_repository, user_repository)

    try:
        board_list = use_case.execute(user_id=current_user.id)

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


@board_router.get("/{board_id}", response_model=BoardListItemResponse)
async def get_board_detail(
    board_id: int,
    current_user: User = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    """게시글 상세 조회"""
    # Use Case 실행
    board_repository = BoardRepositoryImpl(db)
    user_repository = UserRepositoryImpl(db)
    use_case = GetBoardDetail(board_repository, user_repository)

    try:
        board = use_case.execute(board_id=board_id)

        # Dict를 Response 모델로 변환
        return BoardListItemResponse(
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
    except BoardNotFoundException:
        raise HTTPException(status_code=404, detail="Board not found")


@board_router.patch("/{board_id}", response_model=BoardResponse)
async def update_board(
    board_id: int,
    request: UpdateBoardRequest,
    current_user: User = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    """게시글 수정 (작성자만 가능)"""
    # Use Case 실행
    board_repository = BoardRepositoryImpl(db)
    user_repository = UserRepositoryImpl(db)
    use_case = UpdateBoard(board_repository, user_repository)

    try:
        board = use_case.execute(
            board_id=board_id,
            user_id=current_user.id,
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
    except BoardNotFoundException:
        raise HTTPException(status_code=404, detail="Board not found")
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@board_router.delete("/{board_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(
    board_id: int,
    current_user: User = Depends(get_current_user_from_session),
    db: Session = Depends(get_db)
):
    """게시글 삭제 (작성자만 가능)"""
    # Use Case 실행
    board_repository = BoardRepositoryImpl(db)
    use_case = DeleteBoard(board_repository)

    try:
        use_case.execute(board_id=board_id, user_id=current_user.id)
        return None  # 204 No Content
    except BoardNotFoundException:
        raise HTTPException(status_code=404, detail="Board not found")
    except ForbiddenException as e:
        raise HTTPException(status_code=403, detail=str(e))
