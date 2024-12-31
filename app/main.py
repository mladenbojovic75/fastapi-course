
from fastapi import FastAPI
from . import models
from .database import engine, get_db 
from .routers import post, user, auth, vote
from .config import settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# SQLAlchemy create tables
# models.Base.metadata.create_all(bind=engine)
origins = ["*"]
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

@app.get("/")
def root():
    return {"message": "Hello World"}



    
