from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class ResumeData(Base):
    __tablename__ = "resume_data"

    resume_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    file_path = Column(String, nullable=False)
    extracted_text = Column(String, nullable=True)
    fields_extracted = Column(JSON, nullable=True)  # Extracted fields as JSON
    processed_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="resume_data")
