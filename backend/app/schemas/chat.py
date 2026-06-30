from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any

class ChatRequest(BaseModel):
    message: str
    
class ChatResponse(BaseModel):
    session_id: int
    question: str
    answer: str
    source_type: Optional[str] = None
    sources: Optional[List[Dict[str, Any]]] = None
    
# class ChatResponse(BaseModel):
#     session_id: int
#     question: str
#     answer: str

class ChatSessionOut(BaseModel):
    session_id: int
    topic_id: int
    title: str | None = None
    started_at: datetime
    ended_at: datetime | None = None

    class Config:
        orm_mode = True

class ChatMessageOut(BaseModel):
    message_id: int
    sender_type: str
    message: str
    created_at: datetime

    class Config:
        orm_mode = True
