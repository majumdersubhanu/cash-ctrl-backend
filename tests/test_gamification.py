import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_gamification_streaks_empty(client: AsyncClient):
    response = await client.get("/api/v1/gamification/streaks")
    assert response.status_code == 200
    data = response.json()
    assert "current_streak_days" in data
    assert data["current_streak_days"] == 0


@pytest.mark.asyncio
async def test_get_achievements_empty(client: AsyncClient):
