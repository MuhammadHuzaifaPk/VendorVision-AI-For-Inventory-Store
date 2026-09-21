import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "VendorVision AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Google Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    DEFAULT_GEMINI_MODEL: str = "gemini-2.5-flash"
    ENABLE_MOCK_FALLBACK: bool = False

    class Config:
        env_file = ".env"
        extra = "allow"

    def is_ai_configured(self) -> bool:
        return bool(self.GEMINI_API_KEY.strip())

settings = Settings()