# admin_service/routers/admin_users.py
from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_current_admin_user
from utils.auth_client import get_all_users, set_block_status, change_role
from dependencies import get_current_admin_user
=======
from admin_service.utils.auth_users import (
    get_user, get_all_users, set_block_status, change_role, is_admin
)


router = APIRouter()

@router.get("/admin/users")
async def list_users(current_user: dict = Depends(get_current_admin_user)):
    return await get_all_users()

@router.post("/admin/users/{user_id}/block")
async def block_user(user_id: int, current_user: dict = Depends(get_current_admin_user)):
    await set_block_status(user_id, True)
    return {"message": "User blocked"}

@router.post("/admin/users/{user_id}/unblock")
async def unblock_user(user_id: int, current_user: dict = Depends(get_current_admin_user)):
    await set_block_status(user_id, False)
    return {"message": "User unblocked"}

@router.patch("/admin/users/{user_id}/role")
async def update_role(user_id: int, role: str, current_user: dict = Depends(get_current_admin_user)):
    if role not in ["user", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    await change_role(user_id, role)
    return {"message": "Role updated"}
