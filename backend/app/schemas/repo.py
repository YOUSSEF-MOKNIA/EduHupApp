from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import List, Optional

class FileCreate(BaseModel):
    filename: str
    url: str

class DirectoryCreate(BaseModel):
    name: str
    subdirectories: Optional[List['DirectoryCreate']] = []
    files: Optional[List[FileCreate]] = []

class AddFileToDirectory(BaseModel):
    directory_path: List[str]  # Path to the directory, e.g., ['dir1', 'subdir1']

class RepoCreate(BaseModel):
    name: str
    members: List[EmailStr] = []  # List of user emails who are members

class RepoUpdate(BaseModel):
    name: Optional[str] = None
    members: Optional[List[EmailStr]] = None

class DirectoryUpdate(BaseModel):
    name: Optional[str] = None
