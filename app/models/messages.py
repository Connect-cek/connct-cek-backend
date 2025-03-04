from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    recipient_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    content = Column(String, nullable=False)
    conversation_id = Column(String, nullable=True, index=True)  # Optional grouping
    is_request = Column(Boolean, default=False)  # For student-initiated requests
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    sender = relationship(
        "User", foreign_keys=[sender_id], back_populates="sent_messages"
    )
    recipient = relationship(
        "User", foreign_keys=[recipient_id], back_populates="received_messages"
    )
