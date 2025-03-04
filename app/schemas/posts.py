from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class PostBase(BaseModel):
    content: str
    tags: Optional[List[str]] = None


class PostCreate(PostBase):
    pass


class Post(PostBase):
    post_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostWithUser(Post):
    user_name: str
    user_role: str
