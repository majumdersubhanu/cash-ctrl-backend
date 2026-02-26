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
test_engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=None,
)
TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def create_test_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession):
    app.dependency_overrides[get_db] = lambda: db_session

    # Simple dependency override for current user
    async def override_current_user():
        import uuid
        return User(
            id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
            email="test@example.com",
            is_active=True,
            vouch_score=0.0
        )

    from app.core.users import current_active_user

    app.dependency_overrides[current_active_user] = override_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test", follow_redirects=True
    ) as c:
        yield c

    app.dependency_overrides.clear()
