from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    # 데이터베이스 
    database_url: str
    openai_api_key: str
    
    # JWT 설정 
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    
    # API 접두사
    api_prefix: str = "/api"
    
    # Google OAuth2
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: AnyHttpUrl
    
    # 프론트엔드
    frontend_url: AnyHttpUrl

    class Config:
        env_file = ".env"

settings = Settings()
