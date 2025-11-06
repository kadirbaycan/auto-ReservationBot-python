"""Application Settings using Pydantic"""

import os
from typing import List, Optional
from functools import lru_cache

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, validator
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings, Field, validator


class Settings(BaseSettings):
    """Application configuration settings."""

    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")

    # Application
    APP_NAME: str = Field(default="VFS-Automation-Enterprise", env="APP_NAME")
    APP_VERSION: str = Field(default="3.0.0", env="APP_VERSION")

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./data/vfs_automation.db",
        env="DATABASE_URL",
    )
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    DATABASE_ECHO: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis Cache
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    CACHE_TTL: int = Field(default=3600, env="CACHE_TTL")  # seconds

    # Security
    SECRET_KEY: str = Field(
        default="change-this-to-a-secure-random-key-in-production",
        env="SECRET_KEY",
    )
    JWT_SECRET_KEY: str = Field(
        default="change-this-jwt-secret-key",
        env="JWT_SECRET_KEY",
    )
    JWT_ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    JWT_EXPIRATION_MINUTES: int = Field(default=60, env="JWT_EXPIRATION_MINUTES")
    ENCRYPTION_KEY: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")

    # Flask API
    FLASK_HOST: str = Field(default="0.0.0.0", env="FLASK_HOST")
    FLASK_PORT: int = Field(default=5000, env="FLASK_PORT")
    FLASK_DEBUG: bool = Field(default=False, env="FLASK_DEBUG")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5000"],
        env="CORS_ORIGINS",
    )

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_PER_MINUTE: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    RATE_LIMIT_PER_HOUR: int = Field(default=1000, env="RATE_LIMIT_PER_HOUR")

    # VFS Global Configuration
    VFS_BASE_URL: str = Field(
        default="https://visa.vfsglobal.com",
        env="VFS_BASE_URL",
    )
    VFS_BOOKING_URL: str = Field(
        default="https://visa.vfsglobal.com/gnb/pt/prt/book-appointment",
        env="VFS_BOOKING_URL",
    )
    VFS_LOGIN_URL: str = Field(
        default="https://visa.vfsglobal.com/gnb/pt/prt/login",
        env="VFS_LOGIN_URL",
    )
    VFS_MONITORING_DURATION: int = Field(default=4, env="VFS_MONITORING_DURATION")  # minutes
    VFS_MAX_CLIENTS_PER_SESSION: int = Field(default=5, env="VFS_MAX_CLIENTS_PER_SESSION")
    VFS_CHECK_INTERVAL: int = Field(default=30, env="VFS_CHECK_INTERVAL")  # seconds

    # Browser Configuration
    BROWSER_HEADLESS: bool = Field(default=True, env="BROWSER_HEADLESS")
    BROWSER_USE_PLAYWRIGHT: bool = Field(default=True, env="BROWSER_USE_PLAYWRIGHT")
    BROWSER_VIEWPORT_WIDTH: int = Field(default=1920, env="BROWSER_VIEWPORT_WIDTH")
    BROWSER_VIEWPORT_HEIGHT: int = Field(default=1080, env="BROWSER_VIEWPORT_HEIGHT")
    BROWSER_TIMEOUT: int = Field(default=30000, env="BROWSER_TIMEOUT")  # milliseconds

    # Cloudflare Bypass
    CF_BYPASS_ENABLED: bool = Field(default=True, env="CF_BYPASS_ENABLED")
    CF_MAX_ATTEMPTS: int = Field(default=10, env="CF_MAX_ATTEMPTS")
    CF_WAIT_TIMEOUT: int = Field(default=30, env="CF_WAIT_TIMEOUT")  # seconds

    # Proxy Configuration
    PROXY_ENABLED: bool = Field(default=True, env="PROXY_ENABLED")
    PROXY_ROTATION_ENABLED: bool = Field(default=True, env="PROXY_ROTATION_ENABLED")
    PROXY_TEST_TIMEOUT: int = Field(default=10, env="PROXY_TEST_TIMEOUT")
    PROXY_MAX_RETRIES: int = Field(default=3, env="PROXY_MAX_RETRIES")

    # Monitoring & Metrics
    METRICS_ENABLED: bool = Field(default=True, env="METRICS_ENABLED")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    HEALTH_CHECK_ENABLED: bool = Field(default=True, env="HEALTH_CHECK_ENABLED")

    # OpenTelemetry
    OTEL_ENABLED: bool = Field(default=False, env="OTEL_ENABLED")
    OTEL_SERVICE_NAME: str = Field(default="vfs-automation", env="OTEL_SERVICE_NAME")
    OTEL_EXPORTER_ENDPOINT: str = Field(
        default="http://localhost:4317",
        env="OTEL_EXPORTER_ENDPOINT",
    )

    # Notifications
    EMAIL_ENABLED: bool = Field(default=False, env="EMAIL_ENABLED")
    EMAIL_HOST: str = Field(default="smtp.gmail.com", env="EMAIL_HOST")
    EMAIL_PORT: int = Field(default=587, env="EMAIL_PORT")
    EMAIL_USERNAME: Optional[str] = Field(default=None, env="EMAIL_USERNAME")
    EMAIL_PASSWORD: Optional[str] = Field(default=None, env="EMAIL_PASSWORD")
    EMAIL_FROM: str = Field(
        default="noreply@vfs-automation.com",
        env="EMAIL_FROM",
    )

    TELEGRAM_ENABLED: bool = Field(default=False, env="TELEGRAM_ENABLED")
    TELEGRAM_BOT_TOKEN: Optional[str] = Field(default=None, env="TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = Field(default=None, env="TELEGRAM_CHAT_ID")

    # File Upload
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_FILE_EXTENSIONS: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".pdf"],
        env="ALLOWED_FILE_EXTENSIONS",
    )

    # Retry & Circuit Breaker
    MAX_RETRIES: int = Field(default=5, env="MAX_RETRIES")
    RETRY_BACKOFF_FACTOR: float = Field(default=1.5, env="RETRY_BACKOFF_FACTOR")
    CIRCUIT_BREAKER_THRESHOLD: int = Field(default=5, env="CIRCUIT_BREAKER_THRESHOLD")
    CIRCUIT_BREAKER_TIMEOUT: int = Field(default=60, env="CIRCUIT_BREAKER_TIMEOUT")  # seconds

    # Celery (Optional)
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_BROKER_URL",
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        env="CELERY_RESULT_BACKEND",
    )

    # Performance
    ASYNC_WORKERS: int = Field(default=4, env="ASYNC_WORKERS")
    CONNECTION_POOL_SIZE: int = Field(default=20, env="CONNECTION_POOL_SIZE")

    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALLOWED_FILE_EXTENSIONS", pre=True)
    def parse_file_extensions(cls, v):
        """Parse file extensions from string."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.ENVIRONMENT.lower() == "development"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
