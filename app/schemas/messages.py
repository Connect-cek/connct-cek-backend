from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MessageBase(BaseModel):
    content: str
    is_request: Optional[bool] = False


class MessageCreate(MessageBase):
    recipient_id: int


class Message(MessageBase):
    message_id: int
    sender_id: int
    recipient_id: int
    conversation_id: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class MessageWithUsers(Message):
    sender_name: str
    recipient_name: str
