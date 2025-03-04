import random
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.otp import OTPLog
from ..config import settings


class OTPService:
    @staticmethod
    def generate_otp(length: int = 6) -> str:
        """Generate a random OTP code of the specified length."""
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def store_otp(db: Session, email: str, otp: str) -> OTPLog:
        """Store an OTP in the database with an expiry time."""
        expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

        # Remove any existing OTPs for this email
        db.query(OTPLog).filter(OTPLog.email == email).delete()

        # Create new OTP log
        otp_log = OTPLog(email=email, otp_code=otp, expires_at=expires_at)
        db.add(otp_log)
        db.commit()
        db.refresh(otp_log)
        return otp_log

    @staticmethod
    def verify_otp(db: Session, email: str, otp: str) -> bool:
        """Verify an OTP for the given email."""
        otp_log = (
            db.query(OTPLog)
            .filter(
                OTPLog.email == email,
                OTPLog.otp_code == otp,
                OTPLog.expires_at > datetime.utcnow(),
            )
            .first()
        )

        if otp_log:
            # Delete the OTP after successful verification
            db.delete(otp_log)
            db.commit()
            return True
        return False
