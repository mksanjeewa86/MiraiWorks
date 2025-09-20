from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    environment: str = "development"

    # Database
    db_url: str = Field(default="mysql+asyncmy://changeme:changeme@localhost:3306/miraiworks")

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0")

    # S3/MinIO
    s3_endpoint: str = Field(default="http://localhost:9000")
    s3_access_key: str = Field(default="changeme")
    s3_secret_key: str = Field(default="changeme")
    s3_bucket: str = Field(default="miraiworks-files")

    # ClamAV
    clamav_host: str = "localhost"
    clamav_port: int = 3310

    # Email
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    smtp_use_tls: bool = False
    smtp_use_ssl: bool = False
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: str = "noreply@miraiworks.com"
    from_name: str = "MiraiWorks"
    smtp_from: str = "noreply@miraiworks.com"  # Keep for backward compatibility

    # JWT
    jwt_secret: str = Field(default="changeme")
    jwt_access_ttl_min: int = 15
    jwt_refresh_ttl_days: int = 30

    # 2FA
    force_2fa_for_admins: bool = False

    # OAuth
    google_oauth_client_id: Optional[str] = None
    google_oauth_client_secret: Optional[str] = None
    ms_oauth_client_id: Optional[str] = None
    ms_oauth_client_secret: Optional[str] = None

    # Calendar Integration
    google_calendar_client_id: Optional[str] = None
    google_calendar_client_secret: Optional[str] = None
    google_calendar_redirect_uri: Optional[str] = None
    outlook_calendar_client_id: Optional[str] = None
    outlook_calendar_client_secret: Optional[str] = None
    outlook_calendar_redirect_uri: Optional[str] = None

    # App
    app_base_url: str = Field(default="http://localhost:3001")

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
if settings.environment.lower() == "test":
    settings.force_2fa_for_admins = False
