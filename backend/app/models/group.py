from models.repo import FileInDB
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class GroupInDB(BaseModel):
    name: str
    admin_id: str  #    User ID of the group admin
    members: List[str] = []  # List of user emails who are members
    sended_files: List[FileInDB] = []  # List of file urls sended in the group
    created_at: Optional[datetime] = datetime.utcnow()
