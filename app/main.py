from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_router
from app.core.auth import auth_backend
from app.core.logging import setup_logging
from app.core.users import fastapi_users
from app.db.init_db import init_db
from app.db.session import engine
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.api.middleware import LoggingMiddleware
from app.core.security import limiter

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    title="CashCtrl API",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(LoggingMiddleware)


@app.get("/")
def root():
    return {"message": "CashCtrl API running"}


@app.get("/health")
async def health_check():
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/api/v1/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1/auth",
    tags=["auth"],
)
