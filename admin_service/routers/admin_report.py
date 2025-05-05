from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas_report import ReportOut, ReportCreate
from utils.post_service import async_delete_post, async_delete_comment
from typing import List
from sqlalchemy.future import select
from models import Report
from routers.auth_report import get_current_admin_user
from datetime import datetime

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

@report_router.post(
    "/reports",
    response_model=ReportOut,
    summary="Создание жалобы",
    description="Позволяет пользователю отправить жалобу"
)
async def create_report(
    report: ReportCreate,
    db: AsyncSession = Depends(get_db)
):
    new_report = Report(
        post_id=report.post_id,
        comment_id=report.comment_id,
        reporter_id=report.reporter_id,
        reason=report.reason,
        created_at=datetime.utcnow()
    )
    db.add(new_report)
    await db.commit()
    await db.refresh(new_report)
    return new_report

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

