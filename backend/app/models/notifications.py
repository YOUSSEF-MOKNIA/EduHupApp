from datetime import datetime
from typing import Optional
from models.user import UserInDB
from bson import ObjectId
from pydantic import BaseModel, EmailStr

class Notification(BaseModel):
    group_id: Optional[str] = None
    repo_id: Optional[str] = None
    sender: str
    reciever: Optional[str] = None
    content: str
    type: str 
    read: bool = False
    timestamp: datetime
    