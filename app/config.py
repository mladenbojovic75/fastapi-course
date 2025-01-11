from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

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
    algorithm: str
    access_token_expire_minutes: int
    root_path: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()

