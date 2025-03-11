from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class InstitutionType(str, Enum):
    PRIVATE = "private"
    GOVERNMENT = "government"


class InstitutionStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class InstitutionBase(BaseModel):
    name: str
    institution_type: InstitutionType
    location: str
    founded_year: Optional[int] = None
    head_name: str
    head_designation: str
    registration_email: EmailStr


class InstitutionCreate(InstitutionBase):
    pass


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    institution_type: Optional[InstitutionType] = None
    location: Optional[str] = None
    founded_year: Optional[int] = None
    head_name: Optional[str] = None
    head_designation: Optional[str] = None
    registration_email: Optional[EmailStr] = None
    status: Optional[InstitutionStatus] = None


class Institution(InstitutionBase):
    institution_id: int
    status: InstitutionStatus = InstitutionStatus.PENDING
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
