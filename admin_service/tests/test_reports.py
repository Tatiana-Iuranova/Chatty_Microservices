import pytest

from admin_service.tests.test_users import ADMIN_TOKEN


@pytest.mark.asyncio
async def test_get_reports(client):
    response = await client.get("http://localhost:8006/reports", headers={"Authorization": ADMIN_TOKEN})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
