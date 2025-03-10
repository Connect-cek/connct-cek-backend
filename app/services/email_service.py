import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from ..config import settings
import logging

logger = logging.getLogger(__name__)


class EmailService:
    @staticmethod
    async def send_email(to_email: str, subject: str, content: str) -> bool:
        try:
            message = MIMEMultipart()
            message["From"] = settings.EMAIL_USERNAME
            message["To"] = to_email
            message["Subject"] = subject

            message.attach(MIMEText(content, "html"))

            server = smtplib.SMTP(settings.EMAIL_SMTP_SERVER, settings.EMAIL_SMTP_PORT)
            server.starttls()
            server.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
            server.send_message(message)
            server.quit()

            logger.info(f"Email sent successfully to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    @staticmethod
    async def send_otp_email(to_email: str, otp: str, expiry_minutes: int) -> bool:
        subject = "Your OTP Code for Connect"
        content = f"""
        <html>
        <body>
            <h2>Your Connect Verification Code</h2>
            <p>Your OTP code is: <strong>{otp}</strong></p>
            <p>This code will expire in {expiry_minutes} minutes.</p>
            <p>If you did not request this code, please ignore this email.</p>
        </body>
        </html>
        """
        return await EmailService.send_email(to_email, subject, content)
