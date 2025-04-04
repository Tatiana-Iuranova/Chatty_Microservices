from pydantic import BaseModel

class SubscriptionBase(BaseModel):
    user_id: int
    follower_id: int

class SubscriptionCreate(SubscriptionBase):
    """Схема для создания подписки (входные данные)"""
    pass

class SubscriptionResponse(SubscriptionBase):
    """Схема ответа при подписке"""
    class Config:
        from_attributes = True