from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from config.database.session import Base


class BoardORM(Base):
    """게시판 ORM 모델"""
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)  # FK will be added later with migrations
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
