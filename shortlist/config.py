"""配置：pydantic-settings，默认值直接可跑。"""

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="SHORTLIST_", extra="ignore")

    db_path: Path = Path("data/shortlist.db")
    port: int = 8006
    llm_base_url: str = "https://api.deepseek.com"
    llm_api_key: str = ""
    llm_model: str = "deepseek-flash"
    llm_timeout: float = 30.0
    webhook_url: str = ""
    TZ: str = "Asia/Shanghai"

    @property
    def llm_enabled(self) -> bool:
        return bool(self.llm_api_key)


settings = Settings()
