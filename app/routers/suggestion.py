from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict
from ..database import get_db
from ..services.suggestion_service import generate_suggestions, get_domain_suggestions
from ..schemas.suggestion import SuggestionResponse, DomainSuggestionResponse

router = APIRouter(
    prefix="/suggestions",
    tags=["suggestions"],
)


@router.get("/{user_id}", response_model=List[SuggestionResponse])
def get_suggestions(
    user_id: int, 
    limit: int = Query(10, description="Maximum number of suggestions to return"),
    db: Session = Depends(get_db)
):
    """Get suggestions for a user based on similar interests"""
    suggestions = generate_suggestions(db, user_id, limit)
    
    if not suggestions:
        return []
    
    return [
        SuggestionResponse(
            user_id=user.user_id,
            name=user.name,
            similarity_score=score,
            email=user.email,
            role=user.role,
            domain=domain,
            matching_tags=matching_tags
        )
        for user, score, domain, matching_tags in suggestions
    ]


@router.get("/{user_id}/by-domain", response_model=Dict[str, List[SuggestionResponse]])
def get_suggestions_by_domain(
    user_id: int,
    limit_per_domain: int = Query(5, description="Maximum number of suggestions per domain"),
    db: Session = Depends(get_db)
):
    """Get suggestions for a user organized by domain"""
    domain_suggestions = get_domain_suggestions(db, user_id, limit_per_domain)
    
    if not domain_suggestions:
        return {}
    
    result = {}
    for domain, suggestions in domain_suggestions.items():
        result[domain] = [
            SuggestionResponse(
                user_id=user.user_id,
                name=user.name,
                similarity_score=score,
                email=user.email,
                role=user.role,
                domain=domain,
                matching_tags=matching_tags
            )
            for user, score, matching_tags in suggestions
        ]
    
    return result