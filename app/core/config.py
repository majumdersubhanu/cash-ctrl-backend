from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENVIRONMENT: str = "dev"

    DEV_DATABASE_URL: str = "sqlite+aiosqlite:///./cashctrl.db"
    PROD_DATABASE_URL: str | None = None

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    @computed_field
    def DATABASE_URL(self) -> str:
        url = self.PROD_DATABASE_URL if self.ENVIRONMENT == "prod" else self.DEV_DATABASE_URL
        if not url:
            return ""

        # Force asyncpg for postgres
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Fix incompatible parameters for asyncpg driver
        if "postgresql+asyncpg://" in url:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(url)
