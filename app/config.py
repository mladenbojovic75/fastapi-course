from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field
from starlette.middleware.base import BaseHTTPMiddleware

load_dotenv()

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = Field(default=8000, gt=0, le=65535)
    database_hostname: str
    database_port:     str
    database_name:     str
    database_username: str
    database_password: str
    secret_key:        str
    # algorithm: str
    # access_token_expire_minutes: int
    root_path: str = ""
    keycloak_url: str = ""
    client_id: str = ""
    realm_name: str = ""
    client_secret: str = ""
    fastapi_app: str = ""
    nginx_url: str = ""
    callback_url: str = ""
    domain: str = ""
    session_lifetime: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()



class HostHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        host = request.headers.get('Host')
        request.scope['headers'] = [(key.encode(), value.encode()) for key, value in request.headers.items()]
        response = await call_next(request)
        return response