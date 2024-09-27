from pydantic import BaseModel, EmailStr
from typing import List, Optional

class GroupCreate(BaseModel):
    name: str
    members: List[EmailStr]  # List of emails of users to add

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    members: Optional[List[EmailStr]] = None

class GroupResponse(BaseModel):
    id: str
    name: str
    admin_id: str
    members: List[EmailStr]

