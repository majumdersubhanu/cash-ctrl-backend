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
