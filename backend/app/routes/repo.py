import os
from typing import List, Optional
from utils.s3 import delete_file_from_s3, upload_file_to_s3
from crud.user import check_members_exist
from crud.repo import insert_repo, update_repo
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from schemas.repo import AddFileToDirectory, DirectoryCreate, FileCreate, RepoCreate, RepoUpdate
from database.session import db
from routes.auth import get_current_user
from models.repo import FileInDB, RepoInDB
from bson import ObjectId
from datetime import datetime
from dotenv import load_dotenv


router = APIRouter()

@router.post("/create", response_model=dict)
async def create_repo(repo: RepoCreate, current_user: dict = Depends(get_current_user)):
    # Initialize lists for valid, invalid, and duplicate users
    valid_members = [current_user["email"]]  # Add the creator as the first member
    non_existent_members = []
    duplicate_members = []
    seen_emails = set(valid_members)  # Add the creator's email to the seen set
    
    # Check if the user already has a repo with the same name
    existing_repo = await db["repositories"].find_one({"name": repo.name, "owner_id": current_user["id"]})
    if existing_repo:
        raise HTTPException(status_code=400, detail="You already have a repository with this name")
    
    # Validate members' emails and check if they exist in the database
    for email in repo.members:
        # Check for duplicates in the provided list
        if email in seen_emails:
            duplicate_members.append(email)
            continue  # Skip adding the duplicate email

        seen_emails.add(email)

    # Check if the members exist in the database
    valid_members, non_existent_members = await check_members_exist(repo.members, current_user)
    
    # Create the repository with valid members (including the creator)
    repo_in_db = RepoInDB(
        name=repo.name,
        owner_id=current_user["id"],
        members=valid_members,  # Include both the creator and valid members
        files= [],  # Assuming no files at repo creation
        directories= [],  # Assuming no directories at repo creation
        created_at= datetime.utcnow()
    )
    
    # Insert repo into the database
    new_repo = await insert_repo(repo_in_db)
    
    # Update the admin's `owned_repos`
    await db["users"].update_one(
        {"_id": ObjectId(current_user["id"])}, 
        {"$push": {"owned_repos": str(new_repo.inserted_id)}}
    )

    # Update each valid member's `member_repos`
    for email in valid_members:
        await db["users"].update_one(
            {"email": email}, 
            {"$push": {"member_repos": str(new_repo.inserted_id)}}
        )

    # Prepare the response message
    response_message = {
        "message": "Repo created successfully",
        "repo_id": str(new_repo.inserted_id)
    }

    # Add additional messages if there were non-existent or duplicate members
    if non_existent_members:
        response_message["non_existent_members"] = non_existent_members
    if duplicate_members:
        response_message["duplicate_members"] = duplicate_members

    return response_message

# pin repo maximum 6
@router.put("/pin/{repo_id}", response_model=dict)
async def pin_repo(repo_id: str, current_user: dict = Depends(get_current_user)):
    # Fetch the repo to ensure it exists
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Check if the repo is already pinned by the user
    if repo_id in current_user["pinned_repos"]:
        raise HTTPException(status_code=400, detail="Repo already pinned")

    # Check if the user has already pinned 5 repos
    if len(current_user["pinned_repos"]) >= 5:
        raise HTTPException(status_code=400, detail="You can only pin a maximum of 5 repos")

    # Update the user's `pinned_repos`
    await db["users"].update_one(
        {"_id": ObjectId(current_user["id"])}, 
        {"$push": {"pinned_repos": repo_id}}
    )

    return {
        "message": "Repo pinned successfully"
    }

# unpin repo
@router.put("/unpin/{repo_id}", response_model=dict)
async def unpin_repo(repo_id: str, current_user: dict = Depends(get_current_user)):
    # Fetch the repo to ensure it exists
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Check if the repo is already pinned by the user
    if repo_id not in current_user["pinned_repos"]:
        raise HTTPException(status_code=400, detail="Repo not pinned")

    # Update the user's `pinned_repos`
    await db["users"].update_one(
        {"_id": ObjectId(current_user["id"])}, 
        {"$pull": {"pinned_repos": repo_id}}
    )

    return {
        "message": "Repo unpinned successfully"
    }


# get pinned repos
@router.get("/pinned", response_model=list)
async def get_pinned_repos(current_user: dict = Depends(get_current_user)):
    # Fetch all pinned repos by the user
    pinned_repos = await db["repositories"].find({"_id": {"$in": [ObjectId(repo_id) for repo_id in current_user["pinned_repos"]]} }).to_list(length=5)
    
    # Prepare the response
    response = []
    for repo in pinned_repos:
        response.append({
            "id": str(repo["_id"]),
            "name": repo["name"],
            "owner_id": repo["owner_id"],
            "members": repo["members"],
            "files": repo["files"],
            "created_at": repo["created_at"]
        })

    return response

# Update group
@router.put("/update/{repo_id}", response_model=dict)
async def update_repo_details(repo_id: str, repo_update: RepoUpdate, current_user: dict = Depends(get_current_user)):
    # Fetch the group to ensure the user is the admin
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the repo admin can update the repo")

    # Prepare updates
    update_data = {}
    if repo_update.name:
        update_data["name"] = repo_update.name
    
    if repo_update.members:
        valid_members = []
        non_existent_members = []
        for email in repo_update.members:
            user_in_db = await db["users"].find_one({"email": email})
            # check if the user exists already in the group
            if email in repo["members"]:
                continue  # Skip adding the existing member
            if user_in_db:
                valid_members.append(email)
            else:
                non_existent_members.append(email)
        
        if valid_members:
            # Add valid members to the repo
            update_data["members"] = list(set(repo["members"] + valid_members))
        
        if non_existent_members:
            # Return a message about non-existent members
            return {
                "message": "Repository updated successfully, but some members could not be added.",
                "non_existent_members": non_existent_members
            }
    
    # Update the repo in the database
    update_result = await update_repo(repo_id, update_data)
    
    return {
        "message": "Repository updated successfully"
            }


# delete repo
@router.delete("/delete/{repo_id}", response_model=dict)
async def delete_repo(repo_id: str, current_user: dict = Depends(get_current_user)):
    # Fetch the repo to ensure the user is the admin
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")
    if repo["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the repo admin can delete the repo")

    # Delete the repo from the database
    deletion_result = await db["repositories"].delete_one({"_id": ObjectId(repo_id)})
    
    # Remove the repo from the admin's `owned_repos`
    await db["users"].update_one(
        {"_id": ObjectId(current_user["id"])}, 
        {"$pull": {"owned_repos": repo_id}}
    )

    # Remove the repo from each member's `member_repos`
    for email in repo["members"]:
        await db["users"].update_one(
            {"email": email}, 
            {"$pull": {"member_repos": repo_id}}
        )

    return {
        "message": "Repo deleted successfully"
    }


# delete member from repo
@router.put("/remove_member", response_model=dict)
async def remove_member_from_repo(repo_id: str, member_email: str, current_user: dict = Depends(get_current_user)):
    # Fetch the repo from the database
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Check if the current user is the admin of the repo
    if repo["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the repo admin can remove members")

    # Check if the member to be removed is the admin
    if member_email == current_user["email"]:
        raise HTTPException(status_code=400, detail="You cannot remove yourself from the repo")

    # Check if the member exists in the repo
    if member_email not in repo["members"]:
        raise HTTPException(status_code=400, detail="Member not found in the repo")

    # Remove the member from the repo
    update_result = await db["repositories"].update_one(
        {"_id": ObjectId(repo_id)}, 
        {"$pull": {"members": member_email}}
    )

    # Remove the repo from the member's `member_repos`
    await db["users"].update_one(
        {"email": member_email}, 
        {"$pull": {"member_repos": repo_id}}
    )
 
    return {
        "message": "Member removed successfully"
    } 

# add member to repo
@router.put("/add_member", response_model=dict)
async def add_member_to_repo(repo_id: str, member_email: str, current_user: dict = Depends(get_current_user)):
    # Fetch the repo from the database
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Check if the current user is the admin of the repo
    if repo["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Only the repo admin can add members")

    # Check if the member to be added is already in the repo
    if member_email in repo["members"]:
        raise HTTPException(status_code=400, detail="Member already exists in the repo")

    # Check if the member exists in the database
    user_in_db = await db["users"].find_one({"email": member_email})
    if not user_in_db:
        raise HTTPException(status_code=404, detail="Member not found")

    # Add the member to the repo
    update_result = await db["repositories"].update_one(
        {"_id": ObjectId(repo_id)}, 
        {"$push": {"members": member_email}}
    )

    # Add the repo to the member's `member_repos`
    await db["users"].update_one(
        {"email": member_email}, 
        {"$push": {"member_repos": repo_id}}
    )


    return {
        "message": "Member added successfully"
    }

# get all repos
@router.get("/all", response_model=list)
async def get_all_repos(current_user: dict = Depends(get_current_user)):
    # Fetch all repos where the current user is a member
    repos = await db["repositories"].find({"members": current_user["email"]}).to_list(length=1000)
    
    # Prepare the response
    response = []
    for repo in repos:
        response.append({
            "id": str(repo["_id"]),
            "name": repo["name"],
            "owner_id": repo["owner_id"],
            "members": repo["members"],
            "files": repo["files"],
            "created_at": repo["created_at"]
        })

    return response



@router.post("/{repo_id}/add-directory", response_model=dict)
async def add_directory(
    repo_id: str, 
    directory: DirectoryCreate, 
    parent_directory_name: Optional[str] = None,  # Optional parent directory
    current_user: dict = Depends(get_current_user)
):
    # Find the repository by its ID
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id), "owner_id": current_user["id"]})
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or you don't have permission")

    # Recursive function to find a directory
    def find_directory_by_name(directory_list, dir_name):
        for dir in directory_list:
            if dir["name"] == dir_name:
                return dir
            found_dir = find_directory_by_name(dir.get("subdirectories", []), dir_name)
            if found_dir:
                return found_dir
        return None

    # Check if adding to a parent directory or to the root of the repository
    if parent_directory_name:
        parent_directory = find_directory_by_name(repo["directories"], parent_directory_name)
        if not parent_directory:
            raise HTTPException(status_code=404, detail="Parent directory not found")
        
        # Ensure the directory with the same name doesn't already exist in the parent
        for subdir in parent_directory["subdirectories"]:
            if subdir["name"] == directory.name:
                raise HTTPException(status_code=400, detail="Directory already exists")

        # Add the new directory
        new_directory = directory.dict()
        parent_directory["subdirectories"].append(new_directory)
    else:
        # Adding directory at the root level
        for dir in repo["directories"]:
            if dir["name"] == directory.name:
                raise HTTPException(status_code=400, detail="Directory already exists")

        # Add the new directory at the root level
        repo["directories"].append(directory.dict())

    # Update the repository
    await db["repositories"].update_one(
        {"_id": ObjectId(repo_id)},
        {"$set": {"directories": repo["directories"]}}
    )

    return {"message": "Directory added successfully"}

# Load environment variables from .env file
load_dotenv()

# Read allowed file types and max file size from environment variables
ALLOWED_FILE_TYPES = os.getenv("ALLOWED_FILE_TYPES", "").split(",")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # Default to 10 MB if not set


# add file to repository or directory
@router.post("/{repo_id}/add-file", response_model=dict)
async def add_file_to_repo(
    repo_id: str,
    file: UploadFile,
    parent_directory_name: Optional[str] = None,  # Optional: Specify if adding file to a directory
    current_user: dict = Depends(get_current_user)
):
    # Find the repository by its ID
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id), "owner_id": current_user["id"]})
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or you don't have permission")
    
    # # Validate file type
    # if file.content_type not in ALLOWED_FILE_TYPES:
    #     raise HTTPException(status_code=400, detail=f"File type '{file.content_type}' not allowed. Allowed types: {ALLOWED_FILE_TYPES}")

    # Validate file size
    file_size = await file.read()  # Read file content
    if len(file_size) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"File size exceeds the allowed limit of {MAX_FILE_SIZE // (1024 * 1024)} MB")

    # Reset file pointer after reading its size
    await file.seek(0)

    # Recursive function to find a directory by its name
    def find_directory_by_name(directory_list, dir_name):
        for directory in directory_list:
            if directory["name"] == dir_name:
                return directory
            found_dir = find_directory_by_name(directory.get("subdirectories", []), dir_name)
            if found_dir:
                return found_dir
        return None

    # Check if we are adding the file to a directory or directly to the root of the repo
    if parent_directory_name:
        parent_directory = find_directory_by_name(repo["directories"], parent_directory_name)
        if not parent_directory:
            raise HTTPException(status_code=404, detail="Parent directory not found")

        # Ensure that the file with the same name doesn't already exist in the parent directory
        for existing_file in parent_directory.get("files", []):
            if existing_file["filename"] == file.filename:
                raise HTTPException(status_code=400, detail="File already exists in the directory")

        # Upload the file to S3 and get the URL
        file_url = await upload_file_to_s3(file)


        # Create a new file entry
        new_file_data = {
            "filename": file.filename,
            "url": file_url,
            "added_at": datetime.utcnow()
        }

        # Append the file to the parent directory's files
        parent_directory["files"].append(new_file_data)

    else:
        # Ensure the file with the same name doesn't already exist at the root level
        for existing_file in repo.get("files", []):
            if existing_file["filename"] == file.filename:
                raise HTTPException(status_code=400, detail="File already exists in the root directory")

        # Upload the file to S3 and get the URL
        file_url = await upload_file_to_s3(file)

        # Create a new file entry
        new_file_data = {
            "filename": file.filename,
            "url": file_url,
            "added_at": datetime.utcnow()
        }

        # Append the file to the root level of the repository
        repo["files"].append(new_file_data)

    # Update the repository in the database
    await db["repositories"].update_one(
        {"_id": ObjectId(repo_id)},
        {"$set": {"directories": repo["directories"], "files": repo.get("files", [])}}
    )


    return {"message": "File added successfully"}

# get recently added files for 48 hours
# Helper function to collect all files in a repository (including subdirectories)
def collect_all_files(repo):
    all_files = []

    # Add files from root
    if repo.get("files"):
        all_files.extend(repo["files"])

    # Recursive function to collect files from directories
    def collect_from_directory(directory):
        if directory.get("files"):
            all_files.extend(directory["files"])
        for subdirectory in directory.get("subdirectories", []):
            collect_from_directory(subdirectory)

    # Add files from directories
    for directory in repo.get("directories", []):
        collect_from_directory(directory)

    return all_files

# New endpoint to get the 6 most recently added files
@router.get("/recent-files", response_model=List[FileInDB])
async def get_recent_files(current_user: dict = Depends(get_current_user)):
    repos = await db["repositories"].find({"members": current_user["email"]}).to_list(length=5)

    # Collect all files from all repositories
    all_files = []
    for repo in repos:
        all_files.extend(collect_all_files(repo))

    # Sort the files by added_at in descending order
    sorted_files = sorted(all_files, key=lambda file: file["added_at"], reverse=True)

    # Return the 6 most recently added files
    return sorted_files[:5]

# get repo details
@router.get("/{repo_id}", response_model=dict)
async def get_repo(repo_id: str, current_user: dict = Depends(get_current_user)):
    # Fetch the repo from the database
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repo not found")

    # Check if the current user is a member of the repo
    if current_user["email"] not in repo["members"]:
        raise HTTPException(status_code=403, detail="You are not a member of this repo")

    # Prepare the response
    response = {
        "name": repo["name"],
        "owner_id": repo["owner_id"],
        "members": repo["members"],
        "files": repo["files"],
        "directories": repo["directories"],
        "created_at": repo["created_at"]
    }

    return response

# count the number of documents in a repository
@router.get("/{repo_id}/count", response_model=dict)
async def count_repo_documents(repo_id: str, current_user: dict = Depends(get_current_user)):
    # Find the repository by its ID
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    # Check if the current user is a member of the repository
    if current_user["email"] not in repo["members"]:
        raise HTTPException(status_code=403, detail="You are not a member of this repository")

    # Count the number of files and directories in the repository
    file_count = len(repo.get("files", []))
    directory_count = len(repo.get("directories", []))
    count = file_count + directory_count  # No need to cast to int as it's already an integer

    # Return the count as a dictionary
    return {"count": count}

# delete directory
@router.delete("/repo/{repo_id}/delete-directory", response_model=dict)
async def delete_directory(repo_id: str, directory_name: str, current_user: dict = Depends(get_current_user)):
    # Find the repository by its ID
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id), "owner_id": current_user["id"]})

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or you don't have permission")

    # Check if the directory exists in the repository
    directory_to_delete = None
    for directory in repo["directories"]:
        if directory["name"] == directory_name:
            directory_to_delete = directory
            break

    if not directory_to_delete:
        raise HTTPException(status_code=404, detail="Directory not found in the repository")

    # Remove the directory from the repository
    await db["repositories"].update_one(
        {"_id": ObjectId(repo_id)},
        {"$pull": {"directories": directory_to_delete}}
    )

    return {"message": "Directory deleted successfully"}

# delete file from repo root or from directory or subdirectory
@router.delete("/repo/{repo_id}/delete-file", response_model=dict)
async def delete_file(repo_id: str, file_name: str, parent_directory_name: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    # Find the repository by its ID
    repo = await db["repositories"].find_one({"_id": ObjectId(repo_id), "owner_id": current_user["id"]})

    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found or you don't have permission")

    # Check if the file exists in the repository
    file_to_delete = None
    if parent_directory_name:
        # Find the parent directory
        parent_directory = None
        for directory in repo["directories"]:
            if directory["name"] == parent_directory_name:
                parent_directory = directory
                break

        if not parent_directory:
            raise HTTPException(status_code=404, detail="Parent directory not found")

        # Find the file in the parent directory
        for file in parent_directory.get("files", []):
            if file["filename"] == file_name:
                file_to_delete = file
                break

        if not file_to_delete:
            raise HTTPException(status_code=404, detail="File not found in the directory")

        # Remove the file from the parent directory
        await db["repositories"].update_one(
            {"_id": ObjectId(repo_id), "directories.name": parent_directory_name},
            {"$pull": {"directories.$.files": file_to_delete}}
        )
    else:
        # Find the file at the root level
        for file in repo.get("files", []):
            if file["filename"] == file_name:
                file_to_delete = file
                break

        if not file_to_delete:
            raise HTTPException(status_code=404, detail="File not found in the repository")

        # Remove the file from the root level of the repository
        await db["repositories"].update_one(
            {"_id": ObjectId(repo_id)},
            {"$pull": {"files": file_to_delete}}
        )

    # Delete the file from S3
    await delete_file_from_s3(file_name)

    return {"message": "File deleted successfully"}