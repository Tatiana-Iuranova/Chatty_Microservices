import pytest


@pytest.mark.asyncio
async def test_get_reports(client):
    response = await client.get("/reports", headers={"Authorization": ADMIN_TOKEN})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
