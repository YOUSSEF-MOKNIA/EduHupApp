from fastapi import APIRouter, Depends
from typing import List
from database.session import db
from models.notifications import Notification
from routes.auth import get_current_user
from bson import ObjectId

router = APIRouter()


@router.get("/notifications", response_model=List[Notification])
async def get_notifications(current_user: dict = Depends(get_current_user)):
    user_email = current_user["email"]

    # Get the groups the user is part of
    user = await db["users"].find_one({"email": user_email}, {"member_groups": 1})
    group_ids = user.get("member_groups", [])

    # Fetch notifications for this user (both personal and group ones)
    notifications = await db["notifications"].find({
        "$or": [
            {"reciever": user_email},  # Personal notifications
            {"group_id": {"$in": group_ids}}  # Group notifications
        ]
    }).sort("timestamp", -1).to_list(None)

    # Format the notifications
    for notification in notifications:
        notification["_id"] = str(notification["_id"])
        notification["group_id"] = str(notification["group_id"]) if notification.get("group_id") else None
        notification["repo_id"] = str(notification["repo_id"]) if notification.get("repo_id") else None


    return notifications



# mark a notification as read
@router.put("/notifications/{notification_id}")
async def mark_notification_as_read(notification_id: str, current_user: dict = Depends(get_current_user)):
    # Update the notification with the given ID to mark it as read
    await db["notifications"].update_one({"_id": ObjectId(notification_id)}, {"$set": {"read": True}})
    
    return {"message": "Notification marked as read!"}

