import pytest

ADMIN_TOKEN = "Bearer valid_admin_token"  # можно сгенерить заранее

@pytest.mark.asyncio
async def test_list_users_as_admin(client):
    response = await client.get("/admin/users", headers={"Authorization": ADMIN_TOKEN})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_block_user(client):
    response = await client.post("/admin/users/1/block", headers={"Authorization": ADMIN_TOKEN})
    assert response.status_code == 200
    assert response.json()["message"] == "User blocked"

# негативный тест проверяет запрет доступа к административному эндпоинту пользователем, не обладающим правами администратора.
@pytest.mark.asyncio
async def test_non_admin_block_forbidden(client):
    response = await client.post("/admin/users/1/block", headers={"Authorization": "Bearer not_admin"})
    assert response.status_code == 403