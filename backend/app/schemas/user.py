# app/schemas/user.py
from pydantic import BaseModel, AnyUrl
from typing import Optional
from datetime import datetime

class UserRead(BaseModel):
    user_id: int
    email: str
    name: Optional[str] = None
    image_url: Optional[str] = None
    oauth_provider: Optional[str] = None
    oauth_subject: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
