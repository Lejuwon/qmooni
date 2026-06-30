from pydantic import BaseModel
from datetime import datetime

class DocumentCreate(BaseModel):
    file_name: str
    file_type: str | None

class DocumentRead(BaseModel):
    document_id: int
    topic_id:     int
    file_name:    str
    file_type:    str | None
    file_url:     str
    uploaded_at:  datetime

    class Config:
        orm_mode = True
