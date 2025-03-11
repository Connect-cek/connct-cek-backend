from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas.institutions import Institution as InstitutionSchema
from ..schemas.institutions import InstitutionCreate, InstitutionUpdate
from ..models.institutions import Institution
from ..utils.auth import get_current_admin

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.post("/", response_model=InstitutionSchema, status_code=status.HTTP_201_CREATED)
async def create_institution(
    institution: InstitutionCreate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Create a new institution (admin only)."""
    # Check if institution with same email already exists
    existing_institution = (
        db.query(Institution)
        .filter(Institution.registration_email == institution.registration_email)
        .first()
    )

    if existing_institution:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution with this registration email already exists",
        )

    # Create new institution
    new_institution = Institution(**institution.dict())
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    return new_institution


@router.get("/", response_model=List[InstitutionSchema])
async def get_institutions(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all institutions."""
    institutions = db.query(Institution).offset(skip).limit(limit).all()
    return institutions


@router.get("/{institution_id}", response_model=InstitutionSchema)
async def get_institution(
    institution_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific institution by ID."""
    institution = (
        db.query(Institution)
        .filter(Institution.institution_id == institution_id)
        .first()
    )
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )
    return institution


@router.put("/{institution_id}", response_model=InstitutionSchema)
async def update_institution(
    institution_id: int,
    institution_update: InstitutionUpdate,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Update an institution (admin only)."""
    db_institution = (
        db.query(Institution)
        .filter(Institution.institution_id == institution_id)
        .first()
    )
    if not db_institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    # Check if updating to an email that already exists
    if (
        institution_update.registration_email
        and institution_update.registration_email != db_institution.registration_email
    ):
        existing = (
            db.query(Institution)
            .filter(
                Institution.registration_email == institution_update.registration_email
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Institution with this registration email already exists",
            )

    # Update institution fields
    for key, value in institution_update.dict(exclude_unset=True).items():
        setattr(db_institution, key, value)

    db.commit()
    db.refresh(db_institution)
    return db_institution


@router.delete("/{institution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_institution(
    institution_id: int,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin),
):
    """Delete an institution (admin only)."""
    institution = (
        db.query(Institution)
        .filter(Institution.institution_id == institution_id)
        .first()
    )
    if not institution:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Institution not found"
        )

    db.delete(institution)
    db.commit()
    return None
