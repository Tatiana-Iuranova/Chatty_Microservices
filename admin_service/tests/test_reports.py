import pytest

@pytest.mark.asyncio
async def test_get_reports(client, admin_token):
    response = await client.get("/reports", headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
