from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional, List
import json
from ..database import get_db
from ..schemas.users import UserRegister, User as UserSchema
from ..schemas.profiles import Profile as ProfileSchema, ProfileUpdate
from ..models.users import User, UserStatus, UserRole
from ..models.profiles import Profile
from ..models.institutions import Institution
from ..utils.auth import get_current_user
from ..services.file_service import FileService
from ..config import settings

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    institution_id: int = Form(...),
    year_of_study: Optional[str] = Form(None),
    course: Optional[str] = Form(None),
    fields_of_interest: Optional[str] = Form(None),  # JSON string
    profile_photo: Optional[UploadFile] = File(None),
    resume: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):
    """Register a new user with optional profile photo and resume."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    
    # Check if institution exists
    institution = db.query(Institution).filter(Institution.institution_id == institution_id).first()
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )
    
    # Verify email domain matches institution's registration email domain
    user_email_domain = email.split('@')[1]
    institution_email_domain = institution.registration_email.split('@')[1]
    
    # For non-admin users, enforce email domain matching
    if role != UserRole.ADMIN and user_email_domain != institution_email_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Email domain must match institution's domain: {institution_email_domain}"
        )

    # Create new user
    if email == settings.ADMIN_EMAIL:
        new_user = User(
            name=name,
            email=email,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            institution_id=institution_id,
        )
    else:
        new_user = User(
            name=name,
            email=email,
            role=role,
            status=UserStatus.PENDING,
            institution_id=institution_id,
        )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Parse fields of interest if provided
    fields_list = None
    if fields_of_interest:
        try:
            fields_list = json.loads(fields_of_interest)
        except json.JSONDecodeError:
            fields_list = [field.strip() for field in fields_of_interest.split(",")]

    # Save profile photo if provided
    profile_photo_path = None
    if profile_photo:
        success, file_path = await FileService.save_file(
            profile_photo, "uploads/photos"
        )
        if success:
            profile_photo_path = file_path

    # Save resume if provided
    resume_path = None
    if resume:
        success, file_path = await FileService.save_file(resume, "uploads/resumes")
        if success:
            resume_path = file_path

    # Create profile
    profile = Profile(
        user_id=new_user.user_id,
        year_of_study=year_of_study,
        course=course,
        fields_of_interest=fields_list,
        profile_photo_url=profile_photo_path,
        resume_url=resume_path,
    )
    db.add(profile)
    db.commit()

    if new_user.role == UserRole.ADMIN:
        return {"message": "Admin account activated successfully"}

    return {
        "message": "User registered successfully and awaiting approval",
        "user_id": new_user.user_id,
    }


@router.get("/profile", response_model=ProfileSchema)
async def get_profile(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Get the current user's profile."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )
    return profile


@router.put("/profile", response_model=ProfileSchema)
async def update_profile(
    profile_update: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile."""
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
        )

    # Update profile fields
    for key, value in profile_update.dict(exclude_unset=True).items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/institution-users", response_model=List[UserSchema])
async def get_institution_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get users from the same institution as the current user."""
    query = db.query(User).filter(
        User.institution_id == current_user.institution_id,
        User.status == UserStatus.ACTIVE,
        User.user_id != current_user.user_id  # Exclude current user
    )
    
    # Filter by role if specified
    if role:
        query = query.filter(User.role == role)
    
    users = query.all()
    return users
