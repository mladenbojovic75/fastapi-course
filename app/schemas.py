from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal, Optional, List


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True
    

class PostCreate(PostBase):
    pass


class UserCreate(BaseModel):
    email: EmailStr
    username: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    class Config:
        #orm_mode = True
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    username: str



class Post(PostBase):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
    class Config:
        #orm_mode = True
        from_attributes = True
        response_model: None

class PostOut(BaseModel):
    Post: Post
    votes: int

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    

class Vote(BaseModel):
    post_id: int
    dir: Literal[0,1]

class PostWithVotes(Post):
    votes: int
    
class UserWithPosts(UserOut):
    posts: List[PostWithVotes]

#This line is necessary for the forward reference in UserOut
# UserOut.update_forward_refs()
UserOut.model_rebuild()