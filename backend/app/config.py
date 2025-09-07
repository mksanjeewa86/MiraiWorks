from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    db_url: str = "mysql+asyncmy://hrms:hrms@localhost:3306/miraiworks"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # S3/MinIO
    s3_endpoint: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket: str = "miraiworks"

    # ClamAV
    clamav_host: str = "localhost"
    clamav_port: int = 3310

    # Email
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_from: str = "noreply@miraiworks.com"

    # JWT
    jwt_secret: str = "development-secret-change-in-production"
    jwt_access_ttl_min: int = 15
    jwt_refresh_ttl_days: int = 30

    # 2FA
    force_2fa_for_admins: bool = True

    # OAuth
    google_oauth_client_id: Optional[str] = None
    google_oauth_client_secret: Optional[str] = None
    ms_oauth_client_id: Optional[str] = None
    ms_oauth_client_secret: Optional[str] = None

    # App
    app_base_url: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
