from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(Text, nullable=False, unique=True)
    name = Column(Text)
    image_url = Column(Text)
    oauth_provider = Column(Text)
    oauth_subject = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())