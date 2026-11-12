import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SentinelAI – Autonomous Real-Time DAST Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sentinelai-super-secret-key-change-in-production-voyagehack-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database (Default to SQLite, compatible with PostgreSQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sentinelai.db")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
    # Safety Engine Policy Defaults
    DEFAULT_RATE_LIMIT_RPS: int = 5
    ALLOWLIST_ONLY: bool = True
    MAX_CONCURRENT_AGENT_TESTS: int = 3
    
    class Config:
        case_sensitive = True

settings = Settings()
