from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from subscription_service.schemas import SubscriptionResponse
from subscription_service.models import Subscription
from subscription_service.database import get_db
import httpx

router = APIRouter()

# Бизнес-логика
async def follow(db: AsyncSession, user_id: int, follower_id: int) -> SubscriptionResponse:
    """Добавляет подписку (follower_id подписывается на user_id)."""
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
    """Удаляет подписку (follower_id отписывается от user_id)."""
    result = await db.execute(
        select(Subscription).filter_by(user_id=user_id, follower_id=follower_id)
    )
    subscription = result.scalars().first()

    if not subscription:
        raise ValueError("Вы не подписаны")

    await db.delete(subscription)
    await db.commit()

    return {"message": "Подписка удалена"}

# Эндпоинты
@router.post("/subscribe/{user_id}")
async def subscribe(user_id: int, follower_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await follow(db, user_id, follower_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/unsubscribe/{user_id}")
async def unsubscribe(user_id: int, follower_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await unfollow(db, user_id, follower_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/subscriptions")
async def subscriptions(follower_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Subscription.user_id).where(Subscription.follower_id == follower_id)
    )
    return result.scalars().all()

@router.get("/followers")
async def followers(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Subscription.follower_id).where(Subscription.user_id == user_id)
    )
    return result.scalars().all()


@router.get("/feed/{user_id}")
async def get_feed(user_id: int, db: AsyncSession = Depends(get_db)):
    # 1. Получаем ID подписок
    result = await db.execute(
        text("SELECT follower_id FROM subscriptions WHERE user_id = :user_id"),
        {"user_id": user_id}
    )
    follower_ids = [row[0] for row in result.fetchall()]

    if not follower_ids:
        return {"posts": []}

    # 2. Делаем запрос к Post Service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://post_service/posts/by_users",  # URL Post-сервиса
                json={"user_ids": follower_ids}
            )
            response.raise_for_status()
            posts = response.json()
    except httpx.HTTPError as e:
        return {"error": f"Post service error: {str(e)}"}

    # 3. Сортировка (если надо)
    sorted_posts = sorted(posts, key=lambda x: x["created_at"], reverse=True)

    return {"posts": sorted_posts}