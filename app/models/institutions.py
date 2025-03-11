from sqlalchemy import Column, Integer, String, Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base
import enum


class InstitutionType(str, enum.Enum):
    PRIVATE = "private"
    GOVERNMENT = "government"


class Institution(Base):
    __tablename__ = "institutions"

    institution_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    institution_type = Column(Enum(InstitutionType), nullable=False)
    location = Column(String, nullable=False)
    founded_year = Column(Integer, nullable=True)
    head_name = Column(String, nullable=False)
    head_designation = Column(String, nullable=False)
    registration_email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    users = relationship("User", back_populates="institution")
