from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from schemas import SubscriptionResponse, PostListResponse
from models import Subscription
from database import get_db
import httpx
import logging
from dependencies import get_current_user

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# ----------- Бизнес-логика -----------

async def follow(db: AsyncSession, user_id: int, follower_id: int) -> SubscriptionResponse:
    if user_id == follower_id:
        raise ValueError("Нельзя подписаться на себя")

    # Проверяем, не подписан ли пользователь уже
    existing_subscription = await db.execute(
        select(Subscription).filter_by(user_id=user_id, follower_id=follower_id)
    )
    if existing_subscription.scalars().first():
        raise ValueError("Вы уже подписаны на этого пользователя")

    subscription = Subscription(user_id=user_id, follower_id=follower_id)

    try:
        db.add(subscription)
        await db.commit()
        logger.info(f"Подписка: {follower_id} на {user_id} успешно добавлена.")
        return SubscriptionResponse(user_id=user_id, follower_id=follower_id)
    except IntegrityError:
        await db.rollback()
        raise ValueError("Ошибка подписки: возможно, вы уже подписаны")
    except Exception as e:
        logger.error(f"Ошибка подписки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обработке подписки")

async def unfollow(db: AsyncSession, user_id: int, follower_id: int) -> dict:
    result = await db.execute(
        select(Subscription).filter_by(user_id=user_id, follower_id=follower_id)
    )
    subscription = result.scalars().first()

    if not subscription:
        raise ValueError("Вы не подписаны")

    await db.delete(subscription)
    await db.commit()

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
    current_user: dict = Depends(get_current_user),
    user_id: int = Path(..., description="ID пользователя, на которого подписываются"),
    follower_id: int = Query(..., description="ID пользователя, который подписывается"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await follow(db, user_id, follower_id)
    except ValueError as e:
        logger.error(f"Ошибка подписки: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Неизвестная ошибка подписки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обработке подписки")

@router.delete(
    "/unsubscribe/{user_id}",
    summary="Отписаться от пользователя",
    description="Позволяет пользователю отписаться от другого пользователя"
)
async def unsubscribe(
    current_user: dict = Depends(get_current_user),
    user_id: int = Path(..., description="ID пользователя, от которого отписываются"),
    follower_id: int = Query(..., description="ID пользователя, который отписывается"),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await unfollow(db, user_id, follower_id)
    except ValueError as e:
        logger.error(f"Ошибка отписки: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Неизвестная ошибка отписки: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при обработке отписки")

@router.get(
    "/subscriptions",
    response_model=list[int],
    summary="Список подписок пользователя",
    description="Получение ID пользователей, на которых подписан пользователь"
)
async def subscriptions(
    current_user: dict = Depends(get_current_user),
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
        current_user: dict = Depends(get_current_user),
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
    current_user: dict = Depends(get_current_user),
    user_id: int = Path(..., description="ID пользователя"), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Subscription.user_id).where(Subscription.follower_id == user_id))
    subscribed_user_ids = result.scalars().all()

    logger.info(f"Полученные ID пользователей: {subscribed_user_ids}")

    if not subscribed_user_ids:
        return {"posts": []}

    try:
        posts = []
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "http://posts_service:8000/posts/by_user",
                params={"user_ids": ",".join(map(str, subscribed_user_ids))}
            )
            response.raise_for_status()
            posts.extend(response.json())

        logger.info(f"Полученные посты: {posts}")
        sorted_posts = sorted(posts, key=lambda x: x.get("created_at", ""), reverse=True)
        return {"posts": sorted_posts}

    except httpx.HTTPError as e:
        logger.error(f"Ошибка запроса к Posts service: {e}")
        raise HTTPException(status_code=502, detail=f"Posts service error: {str(e)}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка при получении ленты: {e}")
        raise HTTPException(status_code=500, detail="Ошибка при получении ленты постов")
