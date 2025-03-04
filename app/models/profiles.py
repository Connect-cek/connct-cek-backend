from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Profile(Base):
    __tablename__ = "profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    year_of_study = Column(String, nullable=True)  # For students
    course = Column(String, nullable=True)
    fields_of_interest = Column(JSON, nullable=True)
    profile_photo_url = Column(String, nullable=True)
    resume_url = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")
