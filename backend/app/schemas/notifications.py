from models.user import UserInDB
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class NotificationCreate(BaseModel):
    group_id: Optional[str] = None  # Use group_id for group notifications
    repo_id: Optional[str] = None  # Use repo_id for repository notifications
    sender: str
    reciever: Optional[str] = None
    content: str
    type: str
    read: bool = False
    timestamp: datetime
    

class NotificationInDB(NotificationCreate):
    id: str
