from pydantic import BaseModel

class SubscriptionResponse(BaseModel):
    user_id: int
    follower_id: int

class SubscriptionBase(BaseModel):
    user_id: int
    follower_id: int