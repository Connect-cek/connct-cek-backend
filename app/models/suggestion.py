from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Index, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Suggestion(Base):
    __tablename__ = "suggestions"

    suggestion_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    suggested_user_id = Column(Integer, ForeignKey("users.user_id"), index=True)
    similarity_score = Column(Float, nullable=False)
    domain = Column(String, nullable=True)  # Domain of the suggestion (e.g., "technical", "academic", "professional")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Create a composite index for faster lookups
    __table_args__ = (
        Index('idx_user_suggested', user_id, suggested_user_id, unique=True),
    )