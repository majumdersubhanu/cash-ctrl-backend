import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_accounts_empty(client: AsyncClient):
    response = await client.get("/api/v1/accounts")
    assert response.status_code == 200
    assert response.json() == []

@pytest.mark.asyncio
async def test_create_account(client: AsyncClient):
    payload = {
        "name": "Checking",
        "type": "BANK",
        "balance": 1000.50,
        "currency": "USD"
    }
    response = await client.post("/api/v1/accounts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Checking"
    assert data["balance"] == 1000.5
    assert data["currency"] == "USD"
    assert "id" in data

@pytest.mark.asyncio
async def test_get_account(client: AsyncClient):
    # First create
    create_response = await client.post("/api/v1/accounts", json={
        "name": "Savings",
