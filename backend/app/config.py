import sys
from functools import lru_cache
from os import getenv
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


if getattr(sys, "frozen", False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parents[1]


def get_env_file() -> Path:
    env_file = getenv("MDT_BACKEND_ENV_FILE")
    if env_file:
        return Path(env_file).expanduser()
    return BASE_DIR / ".env"


ENV_FILE = get_env_file()
HARDCODED_TAVILY_API_KEY = "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"


def default_generated_image_cache_dir() -> Path:
    local_app_data = getenv("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "Market Sales" / "generated-images"
    return Path.home() / ".market-sales" / "generated-images"


class Settings(BaseSettings):
    # 模型切换开关：local=局域网AI一体机, ollama=本地Ollama, bailian=阿里云百炼云端
    model_provider: str = "local"

    # 局域网AI一体机（model_provider=local 时生效）
    local_model_base_url: str = "http://192.168.0.105:8081/v1"
    local_model_name: str = "Qwen3.6-35B-A3B-UD-Q8_K_XL"
    local_model_max_tokens: int = 2048
    local_model_top_p: float = 0.9

    # 本地 Ollama（model_provider=ollama 时生效）
    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_model: str = "llama3.2"

    # 云端模型 — 阿里云百炼（model_provider=bailian 时生效）
    qwen_api_key: SecretStr | None = None
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen-plus"
    qwen_enable_thinking: bool = False

    # Tavily 联网搜索（SEO 关键词和宣传文案生成前注入上下文）
    tavily_api_key: SecretStr | None = None
    tavily_base_url: str = "https://api.tavily.com"
    tavily_search_depth: str = "basic"
    tavily_max_results: int = Field(default=5, ge=1, le=10)
    tavily_timeout_seconds: float = Field(default=30, gt=0)

    # ComfyUI 生图 / 生视频服务
    comfyui_base_url: str = "http://192.168.0.122:8188"
    comfyui_video_base_url: str = "http://192.168.0.122:8188"
    comfyui_timeout_seconds: float = Field(default=600, gt=0)
    generated_image_cache_dir: Path = Field(default_factory=default_generated_image_cache_dir)
    generated_image_cache_max_age_seconds: int = Field(default=31536000, gt=0)

    # 知识库接口服务（独立 FastAPI 服务，端口沿用现有 20090）
    knowledge_base_url: str = "http://192.168.0.250:20090"
    knowledge_base_timeout_seconds: float = Field(default=300, gt=0)

    request_timeout_seconds: float = 300
    cors_allow_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,null"
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
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


def update_env_file(updates: dict[str, str]) -> None:
    """将给定的键值对写入 .env 文件（存在则更新，不存在则追加）。"""
    env_path = ENV_FILE
    env_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()

    written_keys: set[str] = set()
    new_lines: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#") or not stripped:
            new_lines.append(line)
            continue
        if "=" in stripped:
            key = stripped.split("=", 1)[0].strip().upper()
            canonical = key
            if canonical in {k.upper() for k in updates}:
                matched_key = next(k for k in updates if k.upper() == canonical)
                new_lines.append(f"{matched_key.upper()}={updates[matched_key]}")
                written_keys.add(matched_key)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    for key, value in updates.items():
        if key not in written_keys:
            new_lines.append(f"{key.upper()}={value}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def reload_settings() -> Settings:
    """清除缓存并重新加载配置，返回新的 Settings 实例。"""
    get_settings.cache_clear()
    return get_settings()
