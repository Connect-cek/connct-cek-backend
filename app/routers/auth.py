from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.otp import OTPRequest, OTPVerify, OTPResponse
from ..services.otp_service import OTPService
from ..services.email_service import EmailService
from ..utils.auth import create_access_token
from ..models.users import User
from datetime import timedelta
from ..config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/send-otp", response_model=OTPResponse)
async def send_otp(otp_request: OTPRequest, db: Session = Depends(get_db)):
    """Send an OTP to the provided email."""
    # Generate OTP
    otp_code = OTPService.generate_otp()

    # Store OTP in database
    otp_log = OTPService.store_otp(db, otp_request.email, otp_code)

    # Send OTP via email
    email_sent = await EmailService.send_otp_email(
        otp_request.email, otp_code, settings.OTP_EXPIRY_MINUTES
    )

    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send OTP email",
        )

    return {"message": "OTP sent successfully", "expires_at": otp_log.expires_at}


@router.post("/verify-otp")
async def verify_otp(otp_verify: OTPVerify, db: Session = Depends(get_db)):
    """Verify the OTP provided by the user."""
    try:
        is_valid = OTPService.verify_otp(db, otp_verify.email, otp_verify.otp_code)

        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )

        # Check if user exists (for returning users)
        user = db.query(User).filter(User.email == otp_verify.email).first()

        # Generate access token
        access_token_expires = timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": otp_verify.email},
            expires_delta=access_token_expires
        )

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_exists": user is not None,
            "user_status": user.status if user else None,
        }
    except Exception as e:
        print(f"Error in verify_otp: {str(e)}")  # Add logging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )