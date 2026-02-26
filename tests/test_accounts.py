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
        "type": "BANK",
        "balance": 5000.0,
        "currency": "USD"
    })
    acct_id = create_response.json()["id"]

    # Then get
    response = await client.get(f"/api/v1/accounts/{acct_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Savings"

@pytest.mark.asyncio
async def test_update_account(client: AsyncClient):
    create_response = await client.post("/api/v1/accounts", json={
        "name": "Old Name",
        "type": "BANK",
        "balance": 100.0,
        "currency": "USD"
    })
    acct_id = create_response.json()["id"]

    response = await client.patch(f"/api/v1/accounts/{acct_id}", json={
        "name": "New Name",
        "balance": 200.0
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name"
    assert data["balance"] == 200.0

@pytest.mark.asyncio
async def test_delete_account(client: AsyncClient):
    create_response = await client.post("/api/v1/accounts", json={
        "name": "To Delete",
        "type": "WALLET",
        "balance": 10.0,
        "currency": "USD"
    })
    acct_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/accounts/{acct_id}")
    assert response.status_code == 200

    get_res = await client.get(f"/api/v1/accounts/{acct_id}")
    assert get_res.status_code == 404
