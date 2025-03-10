from pydantic import BaseModel
from typing import Optional, List
from ..models.users import UserRole


class SuggestionResponse(BaseModel):
    user_id: int
    name: str
    email: str
    role: UserRole
    similarity_score: float
    domain: Optional[str] = None
    matching_tags: Optional[List[str]] = None
    
    class Config:
        orm_mode = True


class DomainSuggestionResponse(BaseModel):
    domain: str
    suggestions: List[SuggestionResponse]