from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..database import get_db
from ..models.users import User, UserRole, UserStatus
from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode, settings.TOKEN_SECRET_KEY, algorithm=settings.TOKEN_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from the JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.TOKEN_SECRET_KEY, algorithms=[settings.TOKEN_ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account not activated yet"
        )

    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if the current user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource",
        )
    return current_user


def check_institution_access(user: User, target_institution_id: int) -> bool:
    """Check if a user has access to a specific institution."""
    # Admin has access to all institutions
    if user.role == UserRole.ADMIN and user.email == settings.ADMIN_EMAIL:
        return True

    # Other users only have access to their own institution
    return user.institution_id == target_institution_id
