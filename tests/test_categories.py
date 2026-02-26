import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_categories_empty(client: AsyncClient):
    response = await client.get("/api/v1/categories")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_category(client: AsyncClient):
    payload = {
        "name": "Groceries",
        "type": "EXPENSE"
    }
