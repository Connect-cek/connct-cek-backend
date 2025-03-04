from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    ADMIN_EMAIL: str
    DATABASE_URL: str
    EMAIL_SMTP_SERVER: str
    EMAIL_SMTP_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    COLLEGE_ID: str
    OTP_EXPIRY_MINUTES: int = 10
    TOKEN_SECRET_KEY: str
    TOKEN_ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 60
    LLM_API_KEY: Optional[str] = None
    LLM_API_ENDPOINT: Optional[str] = None


settings = Settings()
