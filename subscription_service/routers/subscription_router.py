from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from schemas import SubscriptionResponse, PostListResponse
from models import Subscription
from database import get_db
import httpx
from faststream.rabbit.fastapi import RabbitRouter
from faststream.rabbit import RabbitQueue
import logging

# Подключаем RabbitMQ через FastStream
rabbit_router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")

# Очереди как глобальные константы
USER_SUBSCRIBED_QUEUE = RabbitQueue("user_subscribed")
USER_UNSUBSCRIBED_QUEUE = RabbitQueue("user_unsubscribed")

# Настройка логирования
logger = logging.getLogger(__name__)

router = APIRouter()

# ----------- Бизнес-логика -----------

async def follow(db: AsyncSession, user_id: int, follower_id: int) -> SubscriptionResponse:
    if user_id == follower_id:
        raise ValueError("Нельзя подписаться на себя")

    subscription = Subscription(user_id=user_id, follower_id=follower_id)

    try:
        db.add(subscription)
        await db.commit()
        await rabbit_router.broker.publish(
            {"user_id": user_id, "follower_id": follower_id},
            queue=USER_SUBSCRIBED_QUEUE
        )
        logger.info(f"Подписка: {follower_id} на {user_id} успешно добавлена.")
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
    await rabbit_router.broker.publish(
        {"user_id": user_id, "follower_id": follower_id},
        queue=USER_UNSUBSCRIBED_QUEUE
    )
    logger.info(f"Отписка: {follower_id} от {user_id} выполнена.")
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
        logger.error(f"Ошибка подписки: {e}")
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
        logger.error(f"Ошибка отписки: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/subscriptions",
    response_model=list[int],
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
    "/followers/{user_id}",
    response_model=dict,
    summary="Список подписчиков пользователя",
    description="Получение ID пользователей, которые подписаны на пользователя"
)
async def followers(
        user_id: int = Path(..., description="ID пользователя"),
        db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Subscription.follower_id).where(Subscription.user_id == user_id)
    )
    return {"followers": result.scalars().all()}


@router.get(
    "/feed/{user_id}",
    response_model=PostListResponse,
    summary="Лента постов пользователя",
    description="Посты от пользователей, на которых подписан пользователь"
)
async def get_feed(
    user_id: int = Path(..., description="ID пользователя"),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Subscription.user_id).where(Subscription.follower_id == user_id)
    )
    subscribed_user_ids = result.scalars().all()

    if not subscribed_user_ids:
        return {"posts": []}

    try:
        posts = []
        async with httpx.AsyncClient() as client:
            for uid in subscribed_user_ids:
                response = await client.get(
                    "http://posts_service:8000/posts/by_user",
                    params={"user_ids": subscribed_user_ids}   # передаем все user_ids
                )
                response.raise_for_status()
                posts.extend(response.json())

        sorted_posts = sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)
        return {"posts": sorted_posts}

    except httpx.HTTPError as e:
        logger.error(f"Ошибка запроса к Posts service: {e}")
        raise HTTPException(status_code=502, detail=f"Posts service error: {str(e)}")
