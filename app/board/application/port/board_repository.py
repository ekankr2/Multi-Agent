from abc import ABC, abstractmethod
from typing import List, Optional

from app.board.domain.board import Board


class BoardRepository(ABC):
    """게시판 리포지토리 포트"""

    @abstractmethod
    def save(self, board: Board) -> Board:
        """Board를 저장하고 저장된 Board 반환"""
        pass

    @abstractmethod
    def find_all(self) -> List[Board]:
        """전체 Board 목록을 최신순으로 조회"""
        pass

    @abstractmethod
    def find_by_id(self, board_id: int) -> Optional[Board]:
        """id로 Board 조회"""
        pass

    @abstractmethod
    def update(self, board: Board) -> Board:
        """Board를 업데이트하고 업데이트된 Board 반환"""
        pass