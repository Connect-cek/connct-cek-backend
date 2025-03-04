from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.resume import ResumeData
from ..models.resume import ResumeData as ResumeDataModel
from ..models.profiles import Profile
from ..models.users import User
from ..utils.auth import get_current_user
from ..services.file_service import FileService
from ..services.llm_service import LLMService

router = APIRouter(prefix="/resume", tags=["Resume"])


@router.post("/upload", response_model=ResumeData)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Upload and process a resume."""
    # Check file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported",
        )

    # Save file
    success, file_path = await FileService.save_file(file, "uploads/resumes")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save resume file",
        )

    # Extract text from PDF
    success, extracted_text = await FileService.extract_text_from_pdf(file_path)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to extract text from resume",
        )

    # Process with LLM
    fields_extracted = await LLMService.extract_resume_fields(extracted_text)

    # Check for existing resume data
    existing_resume = (
        db.query(ResumeDataModel)
        .filter(ResumeDataModel.user_id == current_user.user_id)
        .first()
    )

    if existing_resume:
        # Update existing record
        existing_resume.file_path = file_path
        existing_resume.extracted_text = extracted_text
        existing_resume.fields_extracted = fields_extracted
        db.commit()
        db.refresh(existing_resume)
        resume_data = existing_resume
    else:
        # Create new record
        resume_data = ResumeDataModel(
            user_id=current_user.user_id,
            file_path=file_path,
            extracted_text=extracted_text,
            fields_extracted=fields_extracted,
        )
        db.add(resume_data)
        db.commit()
        db.refresh(resume_data)

    # Update user profile with extracted fields
    profile = db.query(Profile).filter(Profile.user_id == current_user.user_id).first()
    if profile and "interests" in fields_extracted.get("extracted_fields", {}):
        profile.fields_of_interest = fields_extracted["extracted_fields"]["interests"]
        profile.resume_url = file_path
        db.commit()

    return resume_data
