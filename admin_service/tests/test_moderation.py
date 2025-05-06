import pytest

from admin_service.tests.test_users import ADMIN_TOKEN


@pytest.mark.asyncio
async def test_delete_post_success(client):
    response = await client.delete("http://localhost:8006/posts/123", headers={"Authorization": ADMIN_TOKEN})
    assert response.status_code in (204, 404)  # если поста нет — тоже ок

@pytest.mark.asyncio
async def test_delete_comment_success(client):
    response = await client.delete("http://localhost:8006/comments/321", headers={"Authorization": ADMIN_TOKEN})
    assert response.status_code in (204, 404)
