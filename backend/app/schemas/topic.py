# app/schemas/topic.py
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class TopicBase(BaseModel):
    title: str
    # description: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    title: Optional[str] = None
    # description: Optional[str] = None
    
class TopicRead(TopicBase):
    topic_id: int
    user_id: int
    created_at: datetime

    class Config:
        orm_mode = True
