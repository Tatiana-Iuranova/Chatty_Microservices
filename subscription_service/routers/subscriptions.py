from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from subscription_service.database import get_db
from subscription_service.models import Subscription
from subscription_service.schemas import SubscriptionResponse

router = APIRouter()

async def follow(db: AsyncSession, user_id: int, follower_id: int) -> SubscriptionResponse:
    """Добавляет подписку (follower_id подписывается на user_id)."""
    if user_id == follower_id:
        raise HTTPException(status_code=400, detail="Нельзя подписаться на себя")

    subscription = Subscription(user_id=user_id, follower_id=follower_id)

    try:
        db.add(subscription)
        await db.commit()
        return SubscriptionResponse(user_id=user_id, follower_id=follower_id)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Вы уже подписаны")

async def unfollow(db: AsyncSession, user_id: int, follower_id: int) -> dict:
    """Удаляет подписку (follower_id отписывается от user_id)."""
    result = await db.execute(select(Subscription).filter_by(user_id=user_id, follower_id=follower_id))
    subscription = result.scalars().first()

    if not subscription:
        raise HTTPException(status_code=400, detail="Вы не подписаны")

    await db.delete(subscription)
    await db.commit()

    return {"message": "Подписка удалена"}

@router.post("/subscribe/{user_id}")
async def subscribe(user_id: int, follower_id: int, db: AsyncSession = Depends(get_db)):
    """Подписаться на пользователя (follower_id подписывается на user_id)."""
    return await follow(db, user_id, follower_id)

@router.delete("/unsubscribe/{user_id}")
async def unsubscribe(user_id: int, follower_id: int, db: AsyncSession = Depends(get_db)):
    """Отписаться от пользователя (follower_id отписывается от user_id)."""
    return await unfollow(db, user_id, follower_id)
