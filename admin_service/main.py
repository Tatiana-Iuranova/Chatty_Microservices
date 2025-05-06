from fastapi import FastAPI
from routers import auth, admin_users

app = FastAPI(
    title="Admin Service API",
    version="1.0.0",
    description="Админка",
    root_path="/admin"
)

# Добавь prefix
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(admin_users.router, prefix="/admin", tags=["admin"])

@app.get("/")
async def root():
    return {"msg": "Admin Service is alive"}
