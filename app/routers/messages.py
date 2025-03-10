from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
import uuid
from ..database import get_db
from ..schemas.messages import MessageCreate, Message, MessageWithUsers
from ..models.messages import Message as MessageModel
from ..models.users import User, UserRole, UserStatus
from ..utils.auth import get_current_user

router = APIRouter(prefix="/messages", tags=["Messages"])


def can_message(sender_role: str, recipient_role: str) -> bool:
    """Check if the sender is allowed to message the recipient based on roles."""
    allowed_combinations = [
        (UserRole.ALUMNI, UserRole.STUDENT),
        (UserRole.STUDENT, UserRole.ALUMNI),
        (UserRole.STUDENT, UserRole.MENTOR),
        (UserRole.MENTOR, UserRole.STUDENT),
        (UserRole.ALUMNI, UserRole.MENTOR),
        (UserRole.MENTOR, UserRole.ALUMNI),
        (UserRole.MENTOR, UserRole.MENTOR),
        (UserRole.ADMIN, UserRole.STUDENT),
        (UserRole.ADMIN, UserRole.ALUMNI),
        (UserRole.ADMIN, UserRole.MENTOR),
        (UserRole.STUDENT, UserRole.ADMIN),
        (UserRole.ALUMNI, UserRole.ADMIN),
        (UserRole.MENTOR, UserRole.ADMIN),
    ]

    return (sender_role, recipient_role) in allowed_combinations


@router.post("/", response_model=Message)
async def send_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Send a message to another user."""
    # Check if recipient exists and is active
    recipient = (
        db.query(User)
        .filter(User.user_id == message.recipient_id, User.status == UserStatus.ACTIVE)
        .first()
    )

    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient not found or not active",
        )

    # Check if messaging is allowed between these roles
    if not can_message(current_user.role, recipient.role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Messaging not allowed between these roles",
        )

    # For student-initiated messages to alumni, mark as request
    is_request = (
        current_user.role == UserRole.STUDENT and recipient.role == UserRole.ALUMNI
    )
    if is_request:
        message.is_request = True

    # Check for existing conversation
    existing_conversation = (
        db.query(MessageModel)
        .filter(
            (
                (MessageModel.sender_id == current_user.user_id)
                & (MessageModel.recipient_id == message.recipient_id)
            )
            | (
                (MessageModel.sender_id == message.recipient_id)
                & (MessageModel.recipient_id == current_user.user_id)
            )
        )
        .first()
    )

    conversation_id = (
        existing_conversation.conversation_id
        if existing_conversation
        else str(uuid.uuid4())
    )

    # Create new message
    new_message = MessageModel(
        sender_id=current_user.user_id,
        recipient_id=message.recipient_id,
        content=message.content,
        conversation_id=conversation_id,
        is_request=message.is_request,
    )

    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


@router.get("/conversations", response_model=Dict[str, List[MessageWithUsers]])
async def get_conversations(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get all conversations for the current user."""
    # Get all messages where user is sender or recipient
    messages = (
        db.query(
            MessageModel,
            User.name.label("sender_name"),
            User.name.label("recipient_name"),
        )
        .join(User, MessageModel.sender_id == User.user_id)
        .filter(
            (MessageModel.sender_id == current_user.user_id)
            | (MessageModel.recipient_id == current_user.user_id)
        )
        .order_by(MessageModel.timestamp.asc())
        .all()
    )

    # Group messages by conversation_id
    conversations = {}
    for message, sender_name, recipient_name in messages:
        if message.conversation_id not in conversations:
            conversations[message.conversation_id] = []

        message_dict = {
            "message_id": message.message_id,
            "sender_id": message.sender_id,
            "recipient_id": message.recipient_id,
            "content": message.content,
            "conversation_id": message.conversation_id,
            "is_request": message.is_request,
            "timestamp": message.timestamp,
            "sender_name": sender_name,
            "recipient_name": recipient_name,
        }
        conversations[message.conversation_id].append(message_dict)

    return conversations
