from http.client import HTTPException
from utils.s3 import delete_profile_picture_from_s3
from database.session import db  # Import the database connection
from bson import ObjectId

# Get user by email
async def get_user_by_email(email: str):
    user = await db["users"].find_one({"email": email})
    return user

# Update user details (password, email, etc.)
async def update_user(user_id: str, user_data: dict):
    update_result = await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
    return update_result

# Update user's password
async def update_user_password(user_id: str, hashed_password: str):
    update_result = await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": {"hashed_password": hashed_password}})
    return update_result

# Delete user by ID
async def delete_user_func(current_user: dict):
    # Delete user from the database
    delete_result = await db["users"].delete_one({"_id": ObjectId(current_user["id"])})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        # Remove user from groups and repos
        await db["groups"].update_many({}, {"$pull": {"members": current_user["id"]}})
        await db["repos"].update_many({}, {"$pull": {"members": current_user["id"]}})

        if current_user.get("profile_picture_url"):
            # Delete user's profile picture from S3
            await delete_profile_picture_from_s3(current_user)
        return True
    

# check if members emails exist in the database
async def check_members_exist(members: list, current_user: dict):
    valid_members = [current_user["email"]]
    non_existent_members = []

    for email in members:
        user_in_db = await db["users"].find_one({"email": email})
        if user_in_db:
            valid_members.append(email)
        else:
            non_existent_members.append(email)
    
    return valid_members, non_existent_members