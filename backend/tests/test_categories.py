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
    response = await client.post("/api/v1/categories", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Groceries"
    assert data["type"] == "EXPENSE"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_subcategory(client: AsyncClient):
    # Parent
    parent_res = await client.post("/api/v1/categories", json={
        "name": "Food",
        "type": "EXPENSE"
    })
    parent_id = parent_res.json()["id"]

    # Child
    child_res = await client.post("/api/v1/categories", json={
        "name": "Fast Food",
        "type": "EXPENSE",
        "parent_id": parent_id
    })
    assert child_res.status_code == 200
    child_data = child_res.json()
    assert child_data["parent_id"] == parent_id
