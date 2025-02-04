from fastapi import Request, Response, HTTPException, Depends, status
from starlette.responses import RedirectResponse
from keycloak import KeycloakOpenID
from jose import jwt
import requests
from datetime import datetime
from . import models
from .database import get_db
from sqlalchemy.orm import Session
from .config import settings



keycloak_openid = KeycloakOpenID(server_url=settings.keycloak_url,
                                  client_id=settings.client_id,
                                  realm_name=settings.realm_name,
                                  client_secret_key=settings.client_secret)

# Redirect to Keycloak for login
def login(request: Request):
    return RedirectResponse(url=keycloak_openid.auth_url(
        redirect_uri=f"{settings.nginx_url}/callback",  # Callback URL after login
        scope="openid email profile",  # Requested scopes
        state=str(request.url)  # For CSRF protection
    ))

# Handle Keycloak callback
def callback(request: Request):
    token = keycloak_openid.token(
        grant_type="authorization_code",
        code=request.query_params.get("code"),
        redirect_uri=f"{settings.nginx_url}/callback" # Callback URL after login
    )
    
    response = Response()

    # Setting cookies with the suggested parameters
    response.set_cookie(
        "access_token", 
        token['access_token'], 
        max_age=settings.session_lifetime, 
        secure=False, 
        samesite='lax', 
        domain=settings.domain
    )
    response.set_cookie(
        "id_token", 
        token['id_token'], 
        max_age=settings.session_lifetime, 
        secure=False, 
        samesite='lax', 
        domain=settings.domain
    )
    response.set_cookie(
        "refresh_token", 
        token['refresh_token'], 
        max_age=settings.session_lifetime, 
        secure=False, 
        samesite='lax', 
        domain=settings.domain
    )

    # Setting headers for redirection
    response.headers["Location"] = f"{settings.nginx_url}/logged_in.html"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.status_code = status.HTTP_302_FOUND
    
    print(f"Cookies set in callback: {response.headers.getlist('Set-Cookie')}")

    return response

def get_token_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return token

async def verify_token(request: Request, response: Response,db: Session=Depends(get_db)):
    try:
        token = request.cookies.get("access_token")
        refresh_token = request.cookies.get("refresh_token")
        if not token or not refresh_token:
            raise HTTPException(status_code=401, detail="You are not logged in. Please log in to access this resource.")

        decoded_token = jwt.get_unverified_claims(token)
        now = datetime.now().timestamp()
        if decoded_token['exp'] < now:  # Token has expired
            try:
                new_token = await refresh_token(request, response)  # Refresh token logic here
                response = keycloak_openid.introspect(new_token, token_type_hint="access_token")
            except Exception:
                raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
        else:
            response = keycloak_openid.introspect(token, token_type_hint="access_token")

        if not response.get('active', False):
            raise HTTPException(status_code=401, detail="Your session is no longer active. Please log in again.")
        
        populate_or_update_user(response, db)
        return response

    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Could not validate credentials: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during token verification: {str(e)}")

async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token not found")

    try:
        new_tokens = keycloak_openid.refresh_token(refresh_token)
        response.set_cookie("access_token", new_tokens['access_token'], httponly=True)
        response.set_cookie("id_token", new_tokens['id_token'], httponly=True)
        return new_tokens['access_token']
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Could not refresh token: {str(e)}")
    
def get_current_user(request: Request, response: Response):
    return verify_token(request, response)

def populate_or_update_user(user_data: dict, db: Session):
    user = db.query(models.User).filter(models.User.email == user_data.get('email')).first()
    if not user:
        new_user = models.User(
            email=user_data.get('email'),
            username=user_data.get('preferred_username'),
            # Populate other fields as needed
        )
        db.add(new_user)
    else:
        # Update existing user data
        user.username = user_data.get('preferred_username')
        # Update other fields as needed
    db.commit()

def get_current_db_user(user_data: dict = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_data.get('username')).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user.id

def logout(request: Request):
    response = Response("Logged out")
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="id_token")  # Clear id_token cookie as well
    response.delete_cookie(key="refresh_token") # Clear refresh_token cookie as well

    id_token = request.cookies.get("id_token")
 
    if id_token:
        logout_url = f"{settings.keycloak_url}/realms/{settings.realm_name}/protocol/openid-connect/logout"
        params = {
            "id_token_hint": id_token
        }

        
        logout_response = requests.get(logout_url, params=params)
        logout_response = requests.get(logout_url)
        if logout_response.status_code != 204:
            print(f"Logout from Keycloak failed with status code: {logout_response.status_code}")

    return RedirectResponse(url=f"{settings.nginx_url}/index.html", status_code=302)

