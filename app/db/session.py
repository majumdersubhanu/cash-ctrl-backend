from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args["check_same_thread"] = False
else:
    # Disable prepared statement cache for production (Neon/PgBouncer compatibility)
    connect_args["prepared_statement_cache_size"] = 0

engine = create_async_engine(DATABASE_URL, connect_args=connect_args, echo=True)

