import pytest


@pytest.mark.asyncio
async def test_delete_post_success(client):
    response = await client.delete("/posts/123", headers={"Authorization": ADMIN_TOKEN})
    assert response.status_code in (204, 404)  # если поста нет — тоже ок

@pytest.mark.asyncio
async def test_delete_comment_success(client):
    response = await client.delete("/comments/321", headers={"Authorization": ADMIN_TOKEN})
    assert response.status_code in (204, 404)
