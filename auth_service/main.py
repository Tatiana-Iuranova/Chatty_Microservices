# main.py
from fastapi import FastAPI
from routers.auth import router as auth_router
from routers.users import router as users_router
from utils.messaging import rabbit_broker  # Импортируем RabbitBroker

app = FastAPI(
    title="AuthService API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    await rabbit_broker.connect()

@app.on_event("shutdown")
async def shutdown_event():
    await rabbit_broker.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Chatty Microservices"}
