from abc import ABC, abstractmethod
from typing import List

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