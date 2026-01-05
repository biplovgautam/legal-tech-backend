from pydantic_settings import BaseSettings
from typing import Literal, List, Union, Any
from pydantic import field_validator


class Settings(BaseSettings):
    APP_NAME: str = "Legal Tech API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    DATABASE_URL: str

    # CORS Settings
    ALLOWED_HOSTS: Union[str, List[str]] = ["*"]

    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, v: Union[str, List[str]]) -> Any:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
