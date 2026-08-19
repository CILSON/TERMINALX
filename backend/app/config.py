"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration — all values are overridable via env vars or `.env`."""

    # ── Database ──────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://terminalx:terminalx@localhost:5432/terminalx"

    # ── Redis ─────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Mock mode ─────────────────────────────────────────────────────────
    USE_MOCK_DATA: bool = True

    # ── External API Keys ─────────────────────────────────────────────────
    GEMINI_API_KEY: str = ""
    NEWSAPI_KEY: str = ""
    ALPHA_VANTAGE_KEY: str = ""
    COINGECKO_API_KEY: str = ""

    # ── CORS ──────────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    # ── Scheduler ─────────────────────────────────────────────────────────
    QUOTE_UPDATE_INTERVAL_MOCK: int = 5       # seconds
    QUOTE_UPDATE_INTERVAL_LIVE: int = 30      # seconds
    NEWS_FETCH_INTERVAL: int = 300            # 5 minutes
    ALERT_CHECK_INTERVAL: int = 10            # seconds

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
