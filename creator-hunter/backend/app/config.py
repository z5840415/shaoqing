"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "Creator Hunter"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # 数据库配置
    DATABASE_URL: str = "postgresql://creator_hunter:password@localhost:5432/creator_hunter"

    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS配置
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Celery配置
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # 自动化配置
    HEADLESS_BROWSER: bool = True
    BROWSER_TIMEOUT: int = 30000
    DEFAULT_MESSAGE_INTERVAL_MIN: int = 30
    DEFAULT_MESSAGE_INTERVAL_MAX: int = 90

    # 安全配置
    MAX_MESSAGES_PER_HOUR: int = 50
    MAX_MESSAGES_PER_DAY: int = 200
    ACCOUNT_HEALTH_CHECK_INTERVAL: int = 3600

    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
