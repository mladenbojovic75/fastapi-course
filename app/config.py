from dotenv import load_dotenv
#import os
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    database_hostname: str
    database_port:     str
    database_name:     str
    database_username: str
    database_password: str
    secret_key:        str
    algorithm: str
    access_token_expire_minutes: int
    
    class Config:
        env_file = ".env"
        #case_sensitive = True

settings = Settings()

