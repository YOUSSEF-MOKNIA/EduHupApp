from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# User model for MongoDB
class UserInDB(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str
    is_active: bool = True
    created_at: Optional[datetime] = datetime.utcnow()
    profile_picture_url: Optional[str] = None  # Add profile picture URL
    owned_groups: List[str] = []  # List of group IDs where the user is the admin
    owned_repos: List[str] = []  # List of repo IDs where the user is the admin
    member_groups: List[str] = []  # List of group IDs where the user is a member
    member_repos: List[str] = []  # List of repo IDs where the user is a member
    pinned_repos: List[str] = []  # List of repo IDs that the user has
    pinned_groups: List[str] = []  # List of group IDs that the user has

# Conversion function (same as before, now also including the profile_picture_url)
def user_db_to_response(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "firstname": user["firstname"],
        "lastname": user["lastname"],
        "username": user["username"],
        "email": user["email"],
        "is_active": user["is_active"],
        "profile_picture_url": user.get("profile_picture_url"),
        "created_at": user["created_at"],
        "owned_groups": user["owned_groups"],
        "owned_repos": user["owned_repos"],
        "member_groups": user["member_groups"],
        "member_repos": user["member_repos"],
        "pinned_repos": user["pinned_repos"],
        "pinned_groups": user["pinned_groups"],
    }
