from datetime import datetime
from http.client import HTTPException
from models.group import GroupInDB
from database.session import db  # Import the database connection
from bson import ObjectId

# Get user by username
async def insert_group(group: GroupInDB):
    new_group = await db["groups"].insert_one(group)
    if new_group:
        return {"message": "Group created successfully", "group_id": str(new_group.inserted_id)}
    else:
        raise HTTPException(status_code=400, detail="Failed to create group")
    
async def update_group(group_id: str, update_data: dict):
    update_result = await db["groups"].update_one({"_id": ObjectId(group_id)}, {"$set": update_data})
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="No changes made")
    return update_result

# Function to delete a group by its ID
async def delete_group(group_id: str) -> bool:
    deletion_result = await db["groups"].delete_one({"_id": ObjectId(group_id)})

    # Check if the deletion was successful
    if deletion_result.deleted_count == 1:
        return True
    return False


# Get group by ID
async def get_group_by_id(group_id: str):
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group


