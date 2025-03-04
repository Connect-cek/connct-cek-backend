from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.users import User as UserSchema
from ..schemas.messages import MessageCreate, Message
from ..models.users import User, UserStatus
from ..models.messages import Message as MessageModel
from ..utils.auth import get_current_admin
import uuid

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/pending-registrations", response_model=List[UserSchema])
async def get_pending_registrations(
    db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)
):
    """Get all pending user registrations."""
    pending_users = db.query(User).filter(User.status == UserStatus.PENDING).all()
    return pending_users


@router.put("/approve-user/{user_id}", response_model=UserSchema)
async def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Approve a pending user."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if user.status != UserStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not in pending status",
        )

    user.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(user)
    return user


@router.delete("/user/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Delete a user account."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}


@router.post("/message", response_model=Message)
async def send_admin_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    """Send a message from admin to a user."""
    # Check if recipient exists
    recipient = db.query(User).filter(User.user_id == message.recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipient not found"
        )

    # Generate a conversation ID if not exists
    # Check for existing conversation between these users
    existing_conversation = (
        db.query(MessageModel)
        .filter(
            (
                (MessageModel.sender_id == current_admin.user_id)
                & (MessageModel.recipient_id == message.recipient_id)
            )
            | (
                (MessageModel.sender_id == message.recipient_id)
                & (MessageModel.recipient_id == current_admin.user_id)
            )
        )
        .first()
    )

    conversation_id = (
        existing_conversation.conversation_id
        if existing_conversation
        else str(uuid.uuid4())
    )

    # Create message
    new_message = MessageModel(
        sender_id=current_admin.user_id,
        recipient_id=message.recipient_id,
        content=message.content,
        conversation_id=conversation_id,
        is_request=False,
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message
