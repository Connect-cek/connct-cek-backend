from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.institutions import Institution as InstitutionSchema
from ..models.institutions import (
    Institution,
    InstitutionType,
    InstitutionStatus,
)
from ..models.users import User, UserStatus
from ..utils.auth import get_current_user
from ..config import settings
from ..schemas.users import User as UserSchema, UserRegister
from pydantic import BaseModel
from sqlalchemy import func

router = APIRouter(prefix="/super-admin", tags=["Super Admin"])


async def get_super_admin(current_user: User = Depends(get_current_user)) -> User:
    """Check if the current user is the super admin."""
    if current_user.email != settings.ADMIN_EMAIL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can access this resource",
        )
    return current_user


@router.get("/institutions/pending", response_model=List[InstitutionSchema])
async def get_pending_institutions(
    db: Session = Depends(get_db), super_admin: User = Depends(get_super_admin)
):
    """Get all pending institution requests."""
    # In a real implementation, you would have a status field for institutions
    # For now, we'll assume all institutions without approved admins are pending

    # Get all institutions
    institutions = db.query(Institution).all()

    # Filter institutions that don't have an approved admin
    pending_institutions = []
    for institution in institutions:
        # Check if institution has any approved admin
        admin_exists = (
            db.query(User)
            .filter(
                User.institution_id == institution.institution_id,
                User.role == "admin",
                User.status == UserStatus.ACTIVE,
            )
            .first()
        )

        if not admin_exists:
            pending_institutions.append(institution)

    return pending_institutions


@router.put("/institutions/{institution_id}/approve", response_model=InstitutionSchema)
async def approve_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    super_admin: User = Depends(get_super_admin),
):
    """Approve an institution by approving its admin."""
    # Find the institution
    institution = (
        db.query(Institution)
        .filter(Institution.institution_id == institution_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    # Find the pending admin for this institution
    admin = (
        db.query(User)
        .filter(
            User.institution_id == institution_id,
            User.role == "admin",
            User.status == UserStatus.PENDING,
        )
        .first()
    )

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No pending admin found for this institution",
        )

    # Approve the admin
    admin.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(admin)

    return institution


@router.get("/stats")
async def get_system_stats(
    db: Session = Depends(get_db), super_admin: User = Depends(get_super_admin)
):
    """Get system-wide statistics for the super admin dashboard."""
    total_institutions = db.query(Institution).count()
    total_users = db.query(User).count()
    pending_users = db.query(User).filter(User.status == UserStatus.PENDING).count()
    active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()

    # Count users by role
    students = db.query(User).filter(User.role == "student").count()
    alumni = db.query(User).filter(User.role == "alumni").count()
    mentors = db.query(User).filter(User.role == "mentor").count()
    admins = db.query(User).filter(User.role == "admin").count()

    # Count institutions by type
    private_institutions = (
        db.query(Institution)
        .filter(Institution.institution_type == InstitutionType.PRIVATE)
        .count()
    )
    government_institutions = (
        db.query(Institution)
        .filter(Institution.institution_type == InstitutionType.GOVERNMENT)
        .count()
    )

    return {
        "total_institutions": total_institutions,
        "total_users": total_users,
        "user_status": {
            "pending": pending_users,
            "active": active_users,
        },
        "user_roles": {
            "students": students,
            "alumni": alumni,
            "mentors": mentors,
            "admins": admins,
        },
        "institution_types": {
            "private": private_institutions,
            "government": government_institutions,
        },
    }


@router.delete("/institutions/{institution_id}")
async def delete_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    super_admin: User = Depends(get_super_admin),
):
    """Delete an institution and all its associated users."""
    institution = (
        db.query(Institution)
        .filter(Institution.institution_id == institution_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    # Delete all users associated with this institution
    db.query(User).filter(User.institution_id == institution_id).delete()

    # Delete the institution
    db.delete(institution)
    db.commit()

    return {"message": "Institution and all associated users deleted successfully"}


@router.get("/users", response_model=List[UserSchema])
async def get_all_users(
    status: Optional[str] = None,
    role: Optional[str] = None,
    institution_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    super_admin: User = Depends(get_super_admin),
):
    """Get all users with optional filtering."""
    query = db.query(User)

    # Apply filters
    if status:
        query = query.filter(User.status == status)

    if role:
        query = query.filter(User.role == role)

    if institution_id:
        query = query.filter(User.institution_id == institution_id)

    # Apply pagination
    users = query.offset(skip).limit(limit).all()
    return users


@router.put("/users/{user_id}/status", response_model=UserSchema)
async def update_user_status(
    user_id: int,
    status: UserStatus,
    db: Session = Depends(get_db),
    super_admin: User = Depends(get_super_admin),
):
    """Update a user's status."""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user.status = status
    db.commit()
    db.refresh(user)
    return user


@router.post("/institutions/{institution_id}/admin", response_model=UserSchema)
async def create_institution_admin(
    institution_id: int,
    admin_data: UserRegister,
    db: Session = Depends(get_db),
    super_admin: User = Depends(get_super_admin),
):
    """Create an admin for an institution."""
    # Check if institution exists
    institution = (
        db.query(Institution)
        .filter(Institution.institution_id == institution_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == admin_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new admin user
    new_admin = User(
        name=admin_data.name,
        email=admin_data.email,
        role="admin",
        status=UserStatus.ACTIVE,  # Auto-approve since super admin is creating
        institution_id=institution_id,
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    # Update institution status to approved
    institution.status = InstitutionStatus.APPROVED
    db.commit()

    return new_admin


class InstitutionWithStats(InstitutionSchema):
    total_users: int
    active_users: int
    pending_users: int
    students_count: int
    alumni_count: int
    mentors_count: int


@router.get("/institutions/{institution_id}/stats", response_model=InstitutionWithStats)
async def get_institution_stats(
    institution_id: int,
    db: Session = Depends(get_db),
    super_admin: User = Depends(get_super_admin),
):
    """Get detailed stats for a specific institution."""
    institution = (
        db.query(Institution)
        .filter(Institution.institution_id == institution_id)
        .first()
    )

    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    # Get user counts
    total_users = (
        db.query(func.count(User.user_id))
        .filter(User.institution_id == institution_id)
        .scalar()
    )

    active_users = (
        db.query(func.count(User.user_id))
        .filter(User.institution_id == institution_id, User.status == UserStatus.ACTIVE)
        .scalar()
    )

    pending_users = (
        db.query(func.count(User.user_id))
        .filter(
            User.institution_id == institution_id, User.status == UserStatus.PENDING
        )
        .scalar()
    )

    students_count = (
        db.query(func.count(User.user_id))
        .filter(User.institution_id == institution_id, User.role == "student")
        .scalar()
    )

    alumni_count = (
        db.query(func.count(User.user_id))
        .filter(User.institution_id == institution_id, User.role == "alumni")
        .scalar()
    )

    mentors_count = (
        db.query(func.count(User.user_id))
        .filter(User.institution_id == institution_id, User.role == "mentor")
        .scalar()
    )

    # Combine institution data with stats
    result = {
        **institution.__dict__,
        "total_users": total_users,
        "active_users": active_users,
        "pending_users": pending_users,
        "students_count": students_count,
        "alumni_count": alumni_count,
        "mentors_count": mentors_count,
    }

    return result
