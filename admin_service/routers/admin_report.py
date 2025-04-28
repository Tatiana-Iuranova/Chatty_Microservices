from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas_report import ReportOut
from utils.post_service import async_delete_post, async_delete_comment
from typing import List
from sqlalchemy.future import select
from models import Report
from routers.auth_report import get_current_admin_user


report_router = APIRouter()

async def get_all_reports(db: AsyncSession):
    result = await db.execute(select(Report))
    return result.scalars().all()

@report_router.get(
    "/reports",
    response_model=List[ReportOut],
    summary="Получение жалоб",
    description="Позволяет администратору получить список жалоб",

)
async def list_reports(
    db: AsyncSession = Depends(get_db)
):
    reports = await get_all_reports(db)
    return reports

@report_router.delete(
    "/posts/{post_id}", status_code=204,
    summary="Удаление поста",
    description="Позволяет администратору удалить пост по его идентификатору.",

)
async def delete_post(post_id: int, user: dict = Depends(get_current_admin_user)):
    status_code, message = await async_delete_post(post_id)
    if status_code != 204:
        raise HTTPException(status_code=status_code, detail=message)
    return

@report_router.delete(
    "/comments/{comment_id}", status_code=204,
    summary="Удаление комментария",
    description="Позволяет администратору удалить комментарий по его идентификатору.",

)
async def delete_comment(comment_id: int, user: dict = Depends(get_current_admin_user)):
    status_code, message = await async_delete_comment(comment_id)
    if status_code != 204:
        raise HTTPException(status_code=status_code, detail=message)
    return