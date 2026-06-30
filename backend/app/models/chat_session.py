from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    session_id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("topics.topic_id", ondelete="SET NULL"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    title = Column(String(200), nullable=True)  # ✅ 제목 추가
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete")