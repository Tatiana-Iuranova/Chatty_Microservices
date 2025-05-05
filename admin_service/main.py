from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter, Logger
from admin_service.routers.admin_report import report_router
from admin_service.routers import admin_users


router = RabbitRouter("amqp://guest:guest@rabbitmq:5672/")
app = FastAPI(
    title="Admin Service API",
    version="1.0.0",
    description="API для управления администрированием",
    openapi_url="/openapi.json",
    docs_url="/docs",
    root_path="/admin",
    root_path_in_servers=True
)

app.include_router(report_router, prefix="/report", tags=["Report"])
app.include_router(admin_users.router)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Admin Service API"}




