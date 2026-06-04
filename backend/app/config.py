import sys
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    local_model_base_url: str = "http://192.168.0.125:8081/v1"
    local_model_name: str = "Qwen3.6-35B-A3B-UD-Q8_K_XL"
    local_model_max_tokens: int = 2048
    local_model_top_p: float = 0.9
    request_timeout_seconds: float = 300
    cors_allow_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,null"
    )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def cors_origin_regex(self) -> str:
        return r"^(https?://(localhost|127\.0\.0\.1)(:\d+)?|null)$"


@lru_cache
def get_settings() -> Settings:
    return Settings()
