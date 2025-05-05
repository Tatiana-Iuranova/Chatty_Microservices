from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportCreate(BaseModel):
    post_id: Optional[int] = None
    comment_id: Optional[int] = None
    reporter_id: Optional[int] = None
    reason: str


class ReportOut(ReportCreate):
    id: int
    created_at: datetime


    model_config = {
        "from_attributes": True
    }