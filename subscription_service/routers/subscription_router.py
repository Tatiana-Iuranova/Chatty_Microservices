from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from schemas import SubscriptionResponse
from models import Subscription
from database import get_db
import httpx
from faststream.rabbit.fastapi import RabbitRouter
from faststream import Event

# Подключаем RabbitMQ через FastStream
rabbit_router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")

router = APIRouter()


# ----------- Бизнес-логика -----------

async def follow(db: AsyncSession, user_id: int, follower_id: int) -> SubscriptionResponse:
    if user_id == follower_id:
        raise ValueError("Нельзя подписаться на себя")

    subscription = Subscription(user_id=user_id, follower_id=follower_id)

    try:
        db.add(subscription)
        await db.commit()
        return SubscriptionResponse(user_id=user_id, follower_id=follower_id)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Вы уже подписаны")


async def unfollow(db: AsyncSession, user_id: int, follower_id: int) -> dict:
    result = await db.execute(
        select(Subscription).filter_by(user_id=user_id, follower_id=follower_id)
    )
    subscription = result.scalars().first()

    if not subscription:
        raise ValueError("Вы не подписаны")

    await db.delete(subscription)
    await db.commit()
    await rabbit_router.publish(
        "user_unsubscribed",
        Event(payload={"user_id": user_id, "follower_id": follower_id})
    )
    return {"message": "Подписка удалена"}



# ----------- Эндпоинты -----------

@router.post(
    "/subscribe/{user_id}",
    response_model=SubscriptionResponse,
    summary="Подписаться на пользователя",
    description="Позволяет пользователю подписаться на другого пользователя"
)
async def subscribe(
    user_id: int = Path(..., description="ID пользователя, на которого подписываются"),
    follower_id: int = Query(..., description="ID пользователя, который подписывается"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await follow(db, user_id, follower_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete(
    "/unsubscribe/{user_id}",
    summary="Отписаться от пользователя",
    description="Позволяет пользователю отписаться от другого пользователя"
)
async def unsubscribe(
    user_id: int = Path(..., description="ID пользователя, от которого отписываются"),
    follower_id: int = Query(..., description="ID пользователя, который отписывается"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await unfollow(db, user_id, follower_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/subscriptions",
    summary="Список подписок пользователя",
    description="Получение ID пользователей, на которых подписан пользователь"
)
async def subscriptions(
    follower_id: int = Query(..., description="ID подписчика"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Subscription.user_id).where(Subscription.follower_id == follower_id)
    )
    return result.scalars().all()


@router.get(
    "/followers",
    summary="Список подписчиков пользователя",
    description="Получение ID пользователей, которые подписаны на пользователя"
)
async def followers(
    user_id: int = Query(..., description="ID пользователя"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Subscription.follower_id).where(Subscription.user_id == user_id)
    )
    return result.scalars().all()


@router.get(
    "/feed/{user_id}",
    summary="Лента постов пользователя",
    description="Получает посты от пользователей, на которых подписан пользователь"
)
async def get_feed(
    user_id: int = Path(..., description="ID пользователя"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        text("SELECT follower_id FROM subscriptions WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    follower_ids = [row[0] for row in result.fetchall()]

    if not follower_ids:
        return {"posts": []}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://post_service/posts/by_users",
                json={"user_ids": follower_ids}
            )
            response.raise_for_status()
            posts = response.json()
    except httpx.HTTPError as e:
        return {"error": f"Post service error: {str(e)}"}

    sorted_posts = sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)
    return {"posts": sorted_posts}