import os
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Override the database URL to use an in-memory SQLite for tests
os.environ["ENVIRONMENT"] = "test"
os.environ["DEV_DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from app.main import app
from app.api.deps import get_db
from app.db.base import Base
from app.models.user import User

# Test engine
