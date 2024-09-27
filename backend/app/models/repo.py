from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class FileInDB(BaseModel):
    filename: str
    url: str

class DirectoryInDB(BaseModel):
    name: str
    subdirectories: List['DirectoryInDB'] = []
    files: List[FileInDB] = []

class RepoInDB(BaseModel):
    name: str
    owner_id: str
    members: List[str] = []
    files: Optional[List[FileInDB]] = []  # Top-level files in the repo
    directories: Optional[List[DirectoryInDB]] = []
    created_at: Optional[datetime] = datetime.utcnow()
