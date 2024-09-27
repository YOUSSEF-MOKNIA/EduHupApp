from http.client import HTTPException
from typing import List, Optional
from utils.s3 import upload_file_to_s3
from schemas.repo import FileCreate, RepoCreate
from models.repo import RepoInDB
from database.session import db  # Import the database connection
from bson import ObjectId
from fastapi import UploadFile



async def insert_repo(repo: RepoInDB):
    new_repo = await db["repositories"].insert_one(repo.dict())
    if new_repo:
        return new_repo
    else:
        raise HTTPException(status_code=400, detail="Failed to create group")
    
async def update_repo(repo_id: str, update_data: dict):
    update_result = await db["repositories"].update_one({"_id": ObjectId(repo_id)}, {"$set": update_data})
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No changes made")
    return update_result

async def delete_repo(repo_id: str):
    deletion_result = await db["repositories"].delete_one({"_id": ObjectId(repo_id)})
    if deletion_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Repo not found")
    return deletion_result

