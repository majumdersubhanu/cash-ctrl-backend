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
            query_params = parse_qs(parsed.query)

            # asyncpg doesn't support 'sslmode', it uses 'ssl'
            if "sslmode" in query_params:
                ssl_mode = query_params.pop("sslmode")[0]
                # asyncpg uses 'ssl' parameter for the mode if it's a string
                query_params["ssl"] = [ssl_mode]

            # Remove other libpq-specific params that asyncpg rejects
            query_params.pop("channel_binding", None)

            # Reconstruct the URL
            new_query = urlencode(query_params, doseq=True)
            url = urlunparse(parsed._replace(query=new_query))

        return url

    model_config = {"env_file": ".env"}


settings = Settings()
