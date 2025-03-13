from datetime import datetime, timedelta
import random
import string
from sqlalchemy.orm import Session
from ..models.otp import OTPLog

class OTPService:
    @staticmethod
    def generate_otp(length=6):
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def store_otp(db: Session, email: str, otp_code: str, expiry_minutes=10):
        existing_otp = db.query(OTPLog).filter(OTPLog.email == email).first()
        if existing_otp:
            db.delete(existing_otp)
            db.commit()

        expires_at = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        otp_log = OTPLog(
            email=email,
            otp_code=otp_code,
            expires_at=expires_at
        )
        db.add(otp_log)
        db.commit()
        db.refresh(otp_log)
        return otp_log

    @staticmethod
    def verify_otp(db: Session, email: str, otp_code: str) -> bool:
        current_time = datetime.utcnow()
        print(f"Verifying OTP for email: {email}")
        print(f"Current time: {current_time}")
        
        otp_log = db.query(OTPLog).filter(
            OTPLog.email == email,
            OTPLog.otp_code == otp_code,
            OTPLog.expires_at > current_time
        ).first()
        
        if not otp_log:
            existing_otp = db.query(OTPLog).filter(OTPLog.email == email).first()
            if existing_otp:
                print(f"Found OTP record - Expires at: {existing_otp.expires_at}, Code matches: {existing_otp.otp_code == otp_code}")
                print(f"Time valid: {existing_otp.expires_at > current_time}")
            else:
                print("No OTP record found for this email")
            return False

        db.delete(otp_log)
        db.commit()
        return True