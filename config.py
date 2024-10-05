from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./helix.db"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    GROQ_API_KEY: str
    
    # Email settings
    # EMAIL_SENDER: str
    # EMAIL_PASSWORD: str
    # SMTP_SERVER: str = "smtp.gmail.com"
    # SMTP_PORT: int = 587

    class Config:
        env_file = ".env"

settings = Settings()