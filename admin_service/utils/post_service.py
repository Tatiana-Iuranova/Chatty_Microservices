import httpx

POST_SERVICE_URL = "http://post-service:8000"

async def async_delete_post(post_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{POST_SERVICE_URL}/posts/{post_id}")
        return response.status_code, response.text

async def async_delete_comment(comment_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.delete(f"{POST_SERVICE_URL}/comments/{comment_id}")
        return response.status_code, response.text