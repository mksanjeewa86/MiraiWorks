from pydantic import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    db_url: str
    
    # Redis
    redis_url: str
    
    # S3/MinIO
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str
    s3_bucket: str
    
    # ClamAV
    clamav_host: str
    clamav_port: int
    
    # Email
    smtp_host: str
    smtp_port: int
    smtp_from: str
    
    # JWT
    jwt_secret: str
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
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()