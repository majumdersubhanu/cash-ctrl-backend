import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_contact(client: AsyncClient):
    payload = {"name": "John Doe", "email": "john@example.com", "phone": "+1234567890"}
    response = await client.post("/api/v1/p2p/contacts", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert "id" in data
    assert data["trust_score"] == 100.0


