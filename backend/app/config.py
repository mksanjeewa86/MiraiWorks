from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    environment: str = "development"

    # Database
    db_url: str = Field(
        default="mysql+asyncmy://changeme:changeme@localhost:3306/miraiworks"
    )

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
    smtp_username: str | None = None
    smtp_password: str | None = None
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
    google_oauth_client_id: str | None = None
    google_oauth_client_secret: str | None = None
    ms_oauth_client_id: str | None = None
    ms_oauth_client_secret: str | None = None

    # Calendar Integration
    google_calendar_client_id: str | None = None
    google_calendar_client_secret: str | None = None
    google_calendar_redirect_uri: str | None = None
    outlook_calendar_client_id: str | None = None
    outlook_calendar_client_secret: str | None = None
    outlook_calendar_redirect_uri: str | None = None

    # App
    app_base_url: str = Field(default="http://localhost:3001")

    # WebRTC/TURN Server
    coturn_host: str = Field(default="localhost")
    coturn_port: int = Field(default=3478)
    coturn_secret: str = Field(default="coturn-secret")

    # Speech-to-Text Service
    stt_service_url: str | None = None
    stt_api_key: str | None = None

    # OpenAI (for transcription/AI features)
    openai_api_key: str | None = None

    # File Upload Settings
    upload_directory: str = Field(default="uploads")
    max_file_size: int = Field(default=25 * 1024 * 1024)  # 25MB in bytes

    model_config = {"env_file": ".env", "case_sensitive": False}

    # Legacy property mappings for backwards compatibility
    @property
    def DATABASE_URL(self) -> str:
        return self.db_url

    @property
    def REDIS_URL(self) -> str:
        return self.redis_url


settings = Settings()
if settings.environment.lower() == "test":
    settings.force_2fa_for_admins = False
