from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from .users import UserRole


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str


class OTPResponse(BaseModel):
    message: str
    expires_at: Optional[datetime] = None
