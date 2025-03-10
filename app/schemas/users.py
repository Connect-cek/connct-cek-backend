from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    ALUMNI = "alumni"
    MENTOR = "mentor"


class UserStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"


class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole


class UserRegister(UserBase):
    year_of_study: Optional[str] = None
    course: Optional[str] = None
    fields_of_interest: Optional[list[str]] = None


class User(UserBase):
    user_id: int
    status: UserStatus
    created_at: datetime

    class Config:
        from_attributes = True
