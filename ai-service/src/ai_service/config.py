"""Application settings loaded from environment variables.

`pydantic-settings` がプロセス起動時に `.env` と環境変数を読み込み、
型安全な `Settings` インスタンスを提供する。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """環境変数から読み込まれるアプリ設定."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # サーバー
    port: int = 8000
    log_level: str = "info"

    # DB / Redis
    database_url: str = "postgresql://reco:reco_password@localhost:5432/reco"
    redis_url: str = "redis://localhost:6379"

    # LLM (optional)
    # 未設定の場合はテンプレベースのフォールバック説明が使われる
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"


settings = Settings()
