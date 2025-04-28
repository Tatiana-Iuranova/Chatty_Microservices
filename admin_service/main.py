from fastapi import FastAPI
from routers.admin_report import report_router
from routers import admin_users


app = FastAPI(
    title="Admin Service API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    root_path="/api"
)

app.include_router(report_router, prefix="/report", tags=["Report"])
app.include_router(admin_users.router)
@app.get("/")
async def read_root():
    return {"message": "Welcome to the Admin Service API"}




