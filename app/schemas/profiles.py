from pydantic import BaseModel
from typing import Optional, List


class ProfileBase(BaseModel):
    year_of_study: Optional[str] = None
    course: Optional[str] = None
    fields_of_interest: Optional[List[str]] = None
    profile_photo_url: Optional[str] = None
    resume_url: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class Profile(ProfileBase):
    profile_id: int
    user_id: int

    class Config:
        from_attributes = True
