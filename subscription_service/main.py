from fastapi import FastAPI
from routers.subscription_router import router as subscription_router
from schemas import SubscriptionResponse
app = FastAPI()
# Подключаем маршруты из отдельных файлов
app.include_router(subscription_router, prefix="/subscriptions", tags=["subscriptions"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Subscription_Services API"}