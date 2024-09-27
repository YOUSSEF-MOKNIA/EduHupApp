from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageInDB(BaseModel):
    group_id: str
    sender_email: str
    content: str
    timestamp: datetime = datetime.utcnow()
