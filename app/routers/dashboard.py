from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from typing import List

router = APIRouter()

@router.get("/dashboard", response_model=List[schemas.UserWithPosts])
def get_dashboard(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    
    # Constructing the response
    users_with_posts = []
    for user in users:
        user_posts = db.query(models.Post).filter(models.Post.owner_id == user.id).all()
        
        # Fetch vote counts for each post
        posts_with_votes = []
        for post in user_posts:
            vote_count = db.query(models.Vote).filter(models.Vote.post_id == post.id).count()
            posts_with_votes.append({
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "published": post.published,
                "created_at": post.created_at,
                "owner_id": post.owner_id,  # Include owner_id
                "owner": schemas.UserOut.from_orm(post.owner),  # Include owner details
                "votes": vote_count
            })
        
        users_with_posts.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "posts": posts_with_votes
        })
    
    return users_with_posts