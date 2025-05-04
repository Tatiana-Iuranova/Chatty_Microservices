from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os
from uuid import uuid4

router = APIRouter()

UPLOAD_DIR = "static"

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # Проверка формата файла
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    # Генерация уникального имени файла
    filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    # Сохранение файла
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": filename,
        "url": f"/static/{filename}"
    }

@router.get("/list")
def list_images():
    files = os.listdir(UPLOAD_DIR)
    image_urls = [f"/static/{file}" for file in files if file.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp"))]
    return {"images": image_urls}