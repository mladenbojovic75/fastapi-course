from starlette.status import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from .. import models, schemas
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from .. import schemas, models, auth
from typing import Dict

router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)


@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote,db: Session = Depends(get_db), current_user: int = Depends(auth.get_current_db_user)) -> Dict[str, str]:
    post = db.query(models.Post).filter(models.Post.id  == vote.post_id).first()
    print(f"post:{post}")
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {vote.post_id} was not found")
    vote_query = db.query(models.Vote).filter(
        models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user)
    found_vote = vote_query.first()
# if dir/direction is 1, user is trying to create a vote for a post
    if (vote.dir == 1):
        if found_vote:
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=f"user with id:{current_user} has alrady voted on post id:{vote.post_id}")
        new_vote = models.Vote(post_id = vote.post_id,user_id=current_user)
        db.add(new_vote)
        db.commit()
        #db.refresh(new_vote)
        return {"message" : "successfully added vote"}
    
# if dir/direction is 0, user is trying to delete a vote for a post
    else:
        if not found_vote:
            raise HTTPException(status_code=HTTP_409_CONFLICT, detail=f"Vote for post id:{vote.post_id} does not exist")
        
        vote_query.delete(synchronize_session=False)
        db.commit()
        return {"message" : "successfully deleted vote"}
