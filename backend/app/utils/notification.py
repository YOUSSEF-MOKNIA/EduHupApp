from datetime import datetime
from models.user import UserInDB
from bson import ObjectId
from database.session import db
from utils.connection_manager import manager

# Create notification for existing group members
async def create_notification_for_group_members(member_emails: list, content: str, group_id: str, sender_email: str):
    notifications = []
    
    for member_email in member_emails:
        # Skip the sender to avoid self-notification
        if member_email == sender_email:
            continue

        notification = {
            "sender": sender_email,
            "reciever": member_email,  # Old member receiving the notification
            "group_id": ObjectId(group_id),
            "content": content,
            "type": "group",
            "read": False,
             
            "timestamp": datetime.utcnow(),
        }
        notifications.append(notification)

    # Insert all notifications in one go for efficiency
    if notifications:
        await db["notifications"].insert_many(notifications)

# Create personal notification for the new member
async def create_personal_notification(new_member_email: str, content: str, group_id: str):
    notification = {
        "sender": "System",
        "reciever": new_member_email,  # New member receiving the notification
        "group_id": ObjectId(group_id),
        "content": content,
        "type": "personal",
        "read": False,
        "timestamp": datetime.utcnow(),
    }

    # Insert the notification into the database
    await db["notifications"].insert_one(notification)


# Create a new notification
async def create_notification(sender: str, content: str, type:str, group_id: str = None, repo_id: str = None, reciever = None):
    # Check if a similar notification already exists (same content, group_id, and type)
    existing_notification = await db["notifications"].find_one({
        "group_id": ObjectId(group_id) if group_id else None,
        "content": content,
        "type": type
    })

    if existing_notification:
        return  # Avoid creating duplicate notifications
    
    notification = {
        "group_id": ObjectId(group_id) if group_id else None,
        "repo_id": ObjectId(repo_id) if repo_id else None,
        "sender": sender,
        "reciever": reciever,
        "content": content,
        "type": type,
        "timestamp": datetime.utcnow()
    }
    # Save the notification to MongoDB
    await db["notifications"].insert_one(notification)

    # Send real-time notification using WebSocket
    if group_id:
        group = await db["groups"].find_one({"_id": ObjectId(group_id)})
        for member_email in group["members"]:
            # Broadcast notification to all group members using WebSocket manager
            await manager.broadcast(f"Notification for {member_email}: {content}")
    elif repo_id:
        repo = await db["repositories"].find_one({"_id": ObjectId(repo_id)})
        for member_email in repo["members"]:
            # Broadcast notification to all repo members using WebSocket manager
            await manager.broadcast(f"Notification for {member_email}: {content}")

async def notify_other_group_members(group_id: str, new_member_email: str, content: str):
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})
    
    # Notify all other group members (exclude the newly added member)
    for member_email in group["members"]:
        if member_email != new_member_email:  # Skip the new member
            await create_notification(sender="System", group_id=group_id, reciever=None, type="group", content=content)
