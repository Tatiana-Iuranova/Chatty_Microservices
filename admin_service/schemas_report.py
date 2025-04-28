from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReportOut(BaseModel):
    id: int
    post_id: Optional[int]
    comment_id: Optional[int]
    reporter_id: Optional[int]
    reason: str
    created_at: datetime


    model_config = {
        "from_attributes": True
    }