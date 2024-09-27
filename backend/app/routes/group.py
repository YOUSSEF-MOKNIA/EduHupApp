from models.repo import FileInDB
from utils.s3 import get_group_files_from_s3, upload_group_file_to_s3
from crud.group import delete_group, insert_group, update_group
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from schemas.group import GroupCreate, GroupUpdate
from database.session import db
from routes.auth import get_current_user
from models.group import GroupInDB
from bson import ObjectId
from datetime import datetime
import os
from dotenv import load_dotenv


router = APIRouter()

# Create group
@router.post("/create", response_model=dict)
async def create_group(group: GroupCreate, current_user: dict = Depends(get_current_user)):
    # Initialize lists for valid, invalid, and duplicate users
    valid_members = [current_user["email"]]  # Add the creator as the first member
    non_existent_members = []
    duplicate_members = []
    seen_emails = set()
    #set() is a Python data structure that stores unique elements.

    # Add the creator to the seen emails set
    seen_emails.add(current_user["email"])

    # Check if the user already has a group with the same name
    existing_group = await db["groups"].find_one({"name": group.name, "admin_id": current_user["id"]})
    if existing_group:
        raise HTTPException(status_code=400, detail="You already have a group with this name")

    # Validate members' emails and check if they exist in the database
    for email in group.members:
        # Check for duplicates in the provided list
        if email in seen_emails:
            duplicate_members.append(email)
            continue  # Skip adding the duplicate email

        seen_emails.add(email)

        # Check if the user exists in the database
        user_in_db = await db["users"].find_one({"email": email})
        if user_in_db:
            valid_members.append(email)
        else:
            non_existent_members.append(email)

    # Create the group document with valid members
    group_in_db = GroupInDB(
        name=group.name,
        admin_id=current_user["id"],
        members=valid_members,  # Include both the creator and valid members
        created_at=datetime.utcnow()
    )

    # Insert group into the database
    new_group = await insert_group(group_in_db.dict())

    # Add the group to the creator's owned groups
    await db["users"].update_one(
        {"_id": ObjectId(current_user["id"])}, 
        {"$push": {"owned_groups": str(new_group["group_id"])}}
    )

    # Add the group to each valid member's `member_groups` field
    for email in valid_members:
        await db["users"].update_one(
            {"email": email}, 
            {"$push": {"member_groups": str(new_group["group_id"])}}
        )

    # Prepare the response message
    response_message = {
        "message": "Group created successfully",
        "group_id": str(new_group["group_id"])
    }

    # Add additional messages if there were non-existent or duplicate members
    if non_existent_members:
        response_message["non_existent_members"] = non_existent_members
    if duplicate_members:
        response_message["duplicate_members"] = duplicate_members

    return response_message


# Update group
@router.put("/update/{group_id}", response_model=dict)
async def update_group(group_id: str, group_update: GroupUpdate, current_user: dict = Depends(get_current_user)):
    # Fetch the group to ensure the user is the admin
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    if group["admin_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the group admin can update the group")

    # Prepare updates
    update_data = {}
    if group_update.name:
        update_data["name"] = group_update.name
    
    if group_update.members:
        valid_members = []
        non_existent_members = []
        for email in group_update.members:
            user_in_db = await db["users"].find_one({"email": email})
            # check if the user exists already in the group
            if email in group["members"]:
                continue  # Skip adding the existing member
            if user_in_db:
                valid_members.append(email)
            else:
                non_existent_members.append(email)
        
        if valid_members:
            # Add valid members to the group
            update_data["members"] = list(set(group["members"] + valid_members))
        
        if non_existent_members:
            # Return a message about non-existent members
            return {
                "message": "Group updated successfully, but some members could not be added.",
                "non_existent_members": non_existent_members
            }
    
    # Update the group in the database
    update_result = await update_group(group_id, update_data)
    
    return {
        "message": "Group updated successfully"
            }


# delete group
@router.delete("/delete/{group_id}", response_model=dict)
async def delete_group(group_id: str, current_user: dict = Depends(get_current_user)):
    # Find the group by ID
    group_in_db = await db["groups"].find_one({"_id": ObjectId(group_id)})
    
    if not group_in_db:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if the current user is the admin of the group
    if group_in_db["admin_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the admin can delete the group")

    # Proceed to delete the group
    deletion_result = await delete_group(group_id)

    # Remove group reference from members' `member_groups` field
    if deletion_result:
        await db["users"].update_many(
            {"member_groups": group_id}, 
            {"$pull": {"member_groups": group_id}}
        )
        return {"message": "Group deleted successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to delete group")

# delete member from group 
@router.put("/remove_member", response_model=dict)
async def remove_member_from_group(group_id: str, member_email: str, current_user: dict = Depends(get_current_user)):
    # Fetch the group from the database
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if the current user is the admin of the group
    if group["admin_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the admin can remove members from the group")
    
    # Check if the member exists in the group
    if member_email not in group["members"]:
        raise HTTPException(status_code=404, detail="Member not found in the group")

    # Check if the admin is trying to remove themselves
    if member_email == current_user["email"]:
        raise HTTPException(status_code=400, detail="Admin cannot remove themselves from the group")

    # Remove the member from the group's members list
    updated_group_members = [email for email in group["members"] if email != member_email]
    
    # Update the group in the database
    deletion_ressult = await db["groups"].update_one(
        {"_id": ObjectId(group_id)},
        {"$set": {"members": updated_group_members}}
    )

    # Remove the group from the user's `member_groups` field
    if deletion_ressult:
        await db["users"].update_one(
            {"email": member_email},
            {"$pull": {"member_groups": group_id}}
        )

    return {"message": "Member removed successfully from the group"}

# add member to group
@router.put("/add_member", response_model=dict)
async def add_member_to_group(group_id: str, member_email: str, current_user: dict = Depends(get_current_user)):
    # Fetch the group from the database
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if the current user is the admin of the group
    if group["admin_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the admin can add members to the group")
    
    # Check if the member already exists in the group
    if member_email in group["members"]:
        raise HTTPException(status_code=400, detail="Member already exists in the group")

    # Check if the member exists in the database
    user_in_db = await db["users"].find_one({"email": member_email})
    if not user_in_db:
        raise HTTPException(status_code=404, detail="There is no user with this email")

    # Add the member to the group's members list
    updated_group_members = list(set(group["members"] + [member_email]))
    
    # Update the group in the database
    update_result = await db["groups"].update_one(
        {"_id": ObjectId(group_id)},
        {"$set": {"members": updated_group_members}}
    )

    # Add the group to the user's `member_groups` field
    if update_result:
        await db["users"].update_one(
            {"email": member_email},
            {"$push": {"member_groups": group_id}}
        )
    
    return {"message": "Member added successfully to the group"}

# get group details
@router.get("/details/{group_id}", response_model=dict)
async def get_group(group_id: str, current_user: dict = Depends(get_current_user)):
    # Fetch the group from the database
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if the user is a member of the group
    if current_user["email"] not in group["members"]:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    # Prepare the response message
    response_message = {
        "group_id": str(group["_id"]),
        "name": group["name"],
        "admin_id": group["admin_id"],
        "members": group["members"],
        "created_at": group["created_at"]
    }

    return response_message

# get group members
@router.get("/members/{group_id}", response_model=dict)
async def get_group_members(group_id: str, current_user: dict = Depends(get_current_user)):
    # Fetch the group from the database
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if the user is a member of the group
    if current_user["email"] not in group["members"]:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    # Prepare the response message
    response_message = {
        "group_id": str(group["_id"]),
        "members": group["members"]
    }

    return response_message

# Leave group 
@router.put("/leave/{group_id}", response_model=dict)
async def leave_group(group_id: str, current_user: dict = Depends(get_current_user)):
    # Fetch the group from the database
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if the user is a member of the group
    if current_user["email"] not in group["members"]:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    # Check if the user is the admin of the group
    if group["admin_id"] == current_user["id"]:
        raise HTTPException(status_code=403, detail="Admin cannot leave the group. Please delete the group instead")

    # Remove the user from the group's members list
    updated_group_members = [email for email in group["members"] if email != current_user["email"]]
    
    # Update the group in the database
    update_result = await db["groups"].update_one(
        {"_id": ObjectId(group_id)},
        {"$set": {"members": updated_group_members}}
    )

    # Remove the group from the user's `member_groups` field
    if update_result:
        await db["users"].update_one(
            {"email": current_user["email"]},
            {"$pull": {"member_groups": group_id}}
        )
    
     # Notify group members about member who left the group
    notification_content = f"{current_user["firstname"]} {current_user["lastname"]} has left the {group['name']} group"
    await create_notification(group_id=group_id, sender="System", content=notification_content)

    return {"message": "You have left the group successfully"}
    
# get all groups
@router.get("/all", response_model=dict)
async def get_all_groups(current_user: dict = Depends(get_current_user)):
    # Fetch all groups where the user is a member
    groups = await db["groups"].find({"members": current_user["email"]}).to_list(length=1000)

    # Prepare the response message
    response_message = []
    for group in groups:
        response_message.append({
            "group_id": str(group["_id"]),
            "name": group["name"],
            "admin_id": group["admin_id"],
            "members": group["members"],
            "created_at": group["created_at"]
        })
    
    # Wrap the list in a dictionary
    return {"groups": response_message}


# Load environment variables from .env file
load_dotenv()

# Read allowed file types and max file size from environment variables
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "").split(",")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # Default to 10 MB if not set


# file upload route
@router.post("/upload_file/{group_id}")
async def upload_file(group_id: str, file: UploadFile, current_user: dict = Depends(get_current_user)):
    # Check if the group exists
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if the user is a member of the group
    if current_user["email"] not in group["members"]:
        raise HTTPException(status_code=403, detail="You are not a member of this group")
    
    # Validate file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(status_code=400, detail=f"File type '{file.content_type}' not allowed. Allowed types: {ALLOWED_FILE_TYPES}")

    # Validate file size
    file_size = await file.read()  # Read file content
    if len(file_size) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds the allowed limit of {MAX_FILE_SIZE // (1024 * 1024)} MB")

    # Reset file pointer after reading its size
    await file.seek(0)
    
    # upload the file to s3 and get the file url
    file_url = await upload_group_file_to_s3(file)

    # Create a new FileInDB instance
    file_InDB = FileInDB(
        filename=file.filename,
        url=file_url
    )
    group["sended_files"].append(file_InDB.dict())

    # Add the file to the group
    await db["groups"].update_one({"_id": ObjectId(group_id)}, {"$set": {"sended_files": group["sended_files"]}})

    return {"message": "File uploaded successfully"}

# Get all files in a group
@router.get("/files/{group_id}", response_model=dict)
async def get_group_files(group_id: str, current_user: dict = Depends(get_current_user)):
    # Check if the group exists
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Check if the user is a member of the group
    if current_user["email"] not in group["members"]:
        raise HTTPException(status_code=403, detail="You are not a member of this group")

    # Get all files in the group
    files = await get_group_files_from_s3(group["sended_files"])

    return {"files": files}