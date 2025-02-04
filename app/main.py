
from fastapi import FastAPI, Request, Response, Depends
from . import auth, config
from .database import get_db 
from .routers import post, vote, user, dashboard
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

origins = ["*"]

app = FastAPI()

#  app.add_middleware(SessionMiddleware, secret_key=settings.secret_key,max_age=int(settings.session_lifetime))
app.add_middleware(config.HostHeaderMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/login")
async def login_route(request: Request):
    response = auth.login(request)
    return response

@app.get("/callback")
async def callback_route(request: Request):
    response = auth.callback(request)
    return response


@app.get("/logout")
async def logout_route(request: Request):
    response = auth.logout(request)
    return response

@app.get("/protected")
async def protected_route(request: Request, response: Response, db: Session = Depends(get_db)):
    print(f"request:{request.cookies}")
    user_data = await auth.verify_token(request, response, db)
    return {"message": "This is a protected route", "user_data": user_data}
