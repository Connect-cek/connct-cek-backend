from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class ResumeBase(BaseModel):
    file_path: str


class ResumeCreate(ResumeBase):
    pass


class ResumeData(ResumeBase):
    resume_id: int
    user_id: int
    extracted_text: Optional[str] = None
    fields_extracted: Optional[Dict[str, Any]] = None
    processed_at: datetime

    class Config:
        from_attributes = True
