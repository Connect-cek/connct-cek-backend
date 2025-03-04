from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base
from datetime import datetime


class OTPLog(Base):
    __tablename__ = "otp_logs"

    otp_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, index=True)
    otp_code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
