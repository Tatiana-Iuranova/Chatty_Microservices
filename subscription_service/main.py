from fastapi import FastAPI
from routers.subscriptions import router as subscription_router
app = FastAPI()


# Подключаем маршруты из отдельных файлов
app.include_router(subscription_router, prefix="/subscriptions", tags=["subscriptions"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Subscription_Services API"}