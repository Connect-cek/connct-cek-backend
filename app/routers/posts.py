from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..schemas.posts import PostCreate, Post, PostWithUser
from ..models.posts import Post as PostModel
from ..models.users import User, UserStatus, UserRole
from ..utils.auth import get_current_user, get_current_admin
from sqlalchemy import or_

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post("/", response_model=Post, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new post."""
    new_post = PostModel(
        user_id=current_user.user_id, content=post.content, tags=post.tags
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/", response_model=List[PostWithUser])
async def get_posts(
    keyword: Optional[str] = None,
    field: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get posts with optional filtering."""
    query = db.query(
        PostModel, User.name.label("user_name"), User.role.label("user_role")
    ).join(User)

    # Filter by institution (except for admin)
    if current_user.role != UserRole.ADMIN:
        query = query.filter(User.institution_id == current_user.institution_id)

    # Apply filters
    if keyword:
        query = query.filter(PostModel.content.ilike(f"%{keyword}%"))

    if field:
        # This assumes tags are stored as an array in PostgreSQL
        query = query.filter(PostModel.tags.contains([field]))

    # Order by most recent first
    query = query.order_by(PostModel.created_at.desc())

    results = query.all()

    # Convert results to response format
    posts = []
    for post, user_name, user_role in results:
        post_dict = {
            "post_id": post.post_id,
            "user_id": post.user_id,
            "content": post.content,
            "tags": post.tags,
            "created_at": post.created_at,
            "user_name": user_name,
            "user_role": user_role,
        }
        posts.append(post_dict)

    return posts


@router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a post."""
    post = db.query(PostModel).filter(PostModel.post_id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    # Allow post deletion only if user is the owner or an admin
    if post.user_id != current_user.user_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    db.delete(post)
    db.commit()
    return {"message": "Post deleted successfully"}
