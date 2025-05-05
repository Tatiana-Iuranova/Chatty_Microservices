import pytest

@pytest.mark.asyncio
async def test_list_users_as_admin(client, admin_token):
    response = await client.get("/admin/users", headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_block_user(client, admin_token):
    response = await client.post("/admin/users/1/block", headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert response.json()["message"] == "User blocked"

@pytest.mark.asyncio
async def test_non_admin_block_forbidden(client):
    response = await client.post("/admin/users/1/block", headers={"Authorization": "Bearer not_admin"})
    assert response.status_code == 403
