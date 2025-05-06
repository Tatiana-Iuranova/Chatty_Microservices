from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ---- Схемы для подписки ----

class SubscriptionResponse(BaseModel):
    user_id: int
    follower_id: int

class SubscriptionBase(BaseModel):
    user_id: int
    follower_id: int

# ---- Схемы для постов ----

class Post(BaseModel):
    id: int
    user_id: int
    content: str
    created_at: Optional[datetime]

class PostListResponse(BaseModel):
    posts: List[Post]
