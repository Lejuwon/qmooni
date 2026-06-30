from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.session import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, unique=True, nullable=False)
    name = Column(Text)
    image_url = Column(Text)
    oauth_provider = Column(Text)
    oauth_subject = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    topics = relationship("Topic", back_populates="user", cascade="all, delete")