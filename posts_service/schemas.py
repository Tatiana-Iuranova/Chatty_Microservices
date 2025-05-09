from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# ---------------------------
# Post Schemas
# ---------------------------
class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    content: Optional[str]

class PostInDB(PostCreate):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime


    model_config = ConfigDict(from_attributes=True)

class PostWithDetails(PostInDB):
    comments: List["CommentInDB"] = []
    likes: List["LikeInDB"] = []


# ---------------------------
# Comment Schemas
# ---------------------------
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int
    user_id: int

class CommentUpdate(BaseModel):
    content: Optional[str]

class CommentInDB(CommentBase):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------
# Like Schemas
# ---------------------------
class LikeBase(BaseModel):
    post_id: int
    user_id: int

class LikeCreate(LikeBase):
    pass

class LikeInDB(LikeBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
