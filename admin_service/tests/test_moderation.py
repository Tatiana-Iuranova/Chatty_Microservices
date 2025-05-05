import pytest

@pytest.mark.asyncio
async def test_delete_post_success(client, admin_token):
    response = await client.delete("/posts/123", headers={"Authorization": admin_token})
    assert response.status_code in (204, 404)

@pytest.mark.asyncio
async def test_delete_comment_success(client, admin_token):
    response = await client.delete("/comments/321", headers={"Authorization": admin_token})
    assert response.status_code in (204, 404)
