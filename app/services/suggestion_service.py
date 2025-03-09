from sqlalchemy.orm import Session
from collections import Counter
from typing import List, Dict, Set, Tuple, Optional
import math
from ..models.users import User
from ..models.profiles import Profile
from ..models.posts import Post
from ..models.suggestion import Suggestion


# Define domains and their associated tags
DOMAIN_TAGS = {
    "technical": [
        "programming", "coding", "software", "development", "web", "mobile", 
        "app", "data", "ai", "ml", "machine learning", "deep learning", 
        "cloud", "devops", "backend", "frontend", "fullstack", "database",
        "python", "java", "javascript", "react", "node", "angular", "vue",
        "aws", "azure", "gcp", "docker", "kubernetes", "microservices"
    ],
    "academic": [
        "research", "paper", "thesis", "study", "education", "learning",
        "teaching", "course", "university", "college", "school", "degree",
        "phd", "masters", "bachelors", "professor", "student", "academic",
        "science", "math", "physics", "chemistry", "biology", "literature"
    ],
    "professional": [
        "career", "job", "work", "industry", "business", "corporate",
        "startup", "entrepreneurship", "management", "leadership", "hr",
        "recruitment", "interview", "resume", "cv", "portfolio", "networking",
        "mentor", "mentorship", "internship", "project", "collaboration"
    ],
    "creative": [
        "design", "art", "music", "writing", "photography", "video",
        "film", "animation", "graphic", "ux", "ui", "user experience",
        "creative", "portfolio", "illustration", "drawing", "painting"
    ]
}


def identify_domain(tag: str) -> Optional[str]:
    """Identify which domain a tag belongs to"""
    tag_lower = tag.lower()
    for domain, tags in DOMAIN_TAGS.items():
        if any(keyword in tag_lower for keyword in tags):
            return domain
    return None


def calculate_tag_similarity(user_tags: List[str], other_tags: List[str]) -> Tuple[float, List[str]]:
    """Calculate Jaccard similarity between two tag sets and return matching tags"""
    if not user_tags or not other_tags:
        return 0.0, []
    
    set1, set2 = set(user_tags), set(other_tags)
    intersection = set1.intersection(set2)
    union = set1.union(set2)
    
    matching_tags = list(intersection)
    similarity = len(intersection) / len(union) if union else 0.0
    
    return similarity, matching_tags


def get_user_tags(db: Session, user_id: int) -> Dict[str, List[str]]:
    """Collect all tags from a user's posts and profile interests, organized by domain"""
    all_tags = set()
    domain_tags = {domain: [] for domain in DOMAIN_TAGS.keys()}
    domain_tags["other"] = []  # For tags that don't match any domain
    
    # Get tags from posts
    posts = db.query(Post).filter(Post.user_id == user_id).all()
    for post in posts:
        if post.tags:
            all_tags.update(post.tags)
    
    # Get fields of interest from profile
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if profile and profile.fields_of_interest:
        all_tags.update(profile.fields_of_interest)
    
    # Categorize tags by domain
    for tag in all_tags:
        domain = identify_domain(tag)
        if domain:
            domain_tags[domain].append(tag)
        else:
            domain_tags["other"].append(tag)
    
    return domain_tags


def generate_suggestions(db: Session, user_id: int, limit: int = 10) -> List[Tuple[User, float, str, List[str]]]:
    """Generate user suggestions based on tag similarity across domains"""
    # Get the user's tags by domain
    user_domain_tags = get_user_tags(db, user_id)
    all_user_tags = []
    for tags in user_domain_tags.values():
        all_user_tags.extend(tags)
    
    if not all_user_tags:
        return []
    
    # Get all other users
    other_users = db.query(User).filter(User.user_id != user_id).all()
    
    # Calculate similarity scores across domains
    suggestions = []
    for other_user in other_users:
        other_domain_tags = get_user_tags(db, other_user.user_id)
        all_other_tags = []
        for tags in other_domain_tags.values():
            all_other_tags.extend(tags)
        
        # Calculate overall similarity
        overall_score, matching_tags = calculate_tag_similarity(all_user_tags, all_other_tags)
        
        # Calculate domain-specific similarities
        domain_scores = {}
        for domain, user_tags in user_domain_tags.items():
            if user_tags:  # Only consider domains where the user has tags
                other_tags = other_domain_tags.get(domain, [])
                domain_score, domain_matching = calculate_tag_similarity(user_tags, other_tags)
                if domain_score > 0:
                    domain_scores[domain] = (domain_score, domain_matching)
        
        # Determine the primary domain of similarity
        primary_domain = "general"
        max_score = 0
        primary_matching = matching_tags
        
        for domain, (score, domain_matching) in domain_scores.items():
            if score > max_score:
                max_score = score
                primary_domain = domain
                primary_matching = domain_matching
        
        # Only consider users with some similarity
        if overall_score > 0:
            suggestions.append((other_user, overall_score, primary_domain, primary_matching))
    
    # Sort by similarity score (highest first)
    suggestions.sort(key=lambda x: x[1], reverse=True)
    
    # Store suggestions in database
    for user, score, domain, _ in suggestions[:limit]:
        existing = db.query(Suggestion).filter(
            Suggestion.user_id == user_id,
            Suggestion.suggested_user_id == user.user_id
        ).first()
        
        if existing:
            existing.similarity_score = score
            existing.domain = domain
        else:
            db.add(Suggestion(
                user_id=user_id,
                suggested_user_id=user.user_id,
                similarity_score=score,
                domain=domain
            ))
    
    db.commit()
    return suggestions[:limit]


def get_domain_suggestions(db: Session, user_id: int, limit_per_domain: int = 5) -> Dict[str, List[Tuple[User, float, List[str]]]]:
    """Get suggestions organized by domain"""
    # Get all suggestions
    all_suggestions = generate_suggestions(db, user_id, limit=50)  # Get more suggestions to ensure coverage across domains
    
    # Organize by domain
    domain_suggestions = {}
    for user, score, domain, matching_tags in all_suggestions:
        if domain not in domain_suggestions:
            domain_suggestions[domain] = []
        
        if len(domain_suggestions[domain]) < limit_per_domain:
            domain_suggestions[domain].append((user, score, matching_tags))
    
    return domain_suggestions