from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: List[str] = []

    class Config:
        env_file = ".env"
        extra = "ignore" 

settings = Settings()
