from .. import models,  schemas
from typing import  List, Optional
from fastapi import Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from .. import auth

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/",response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(auth.get_current_db_user), 
              limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    posts_query = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).outerjoin(
        models.Vote, models.Vote.post_id == models.Post.id
    ).group_by(models.Post.id).filter(
        models.Post.owner_id == current_user
    ).filter(
        models.Post.title.contains(search)
    ).limit(limit).offset(skip)
    
    posts = posts_query.all()
    
    print(f"Number of posts retrieved: {len(posts)}")
    # Convert SQLAlchemy objects to PostOut schema
    result = [
        schemas.PostOut(
            Post=schemas.Post.from_orm(post[0]),  # post[0] is the Post object
            votes=post[1]  # post[1] is the count of votes
        ) for post in posts
    ]
    
    print(f"Returning: {result}")
    return result

@router.post("/",status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), 
                 current_user: int = Depends(auth.get_current_db_user)) -> schemas.Post:
    print(post)
    new_post = models.Post(owner_id=current_user, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,db: Session = Depends(get_db), 
                current_user: int = Depends(auth.get_current_db_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    if post.owner_id != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
     detail=f"Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

