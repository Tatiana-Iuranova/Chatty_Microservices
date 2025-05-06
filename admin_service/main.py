from fastapi import FastAPI
from faststream.rabbit.fastapi import RabbitRouter, Logger
from routers.admin_report import report_router
from routers import admin_users
from utils.messaging import rabbit_broker


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
app.include_router(admin_users.router,prefix="/admin", tags=["admin"])


@app.on_event("startup")
async def startup_event():
    await rabbit_broker.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await rabbit_broker.close()

app.include_router(admin_users.router)

async def root():
    return {"msg": "Admin Service is alive"}

