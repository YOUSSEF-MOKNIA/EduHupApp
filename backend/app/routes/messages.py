from http.client import HTTPException
from utils.notification import create_notification
from routes.auth import get_current_user
from crud.messages import insert_message
from fastapi import WebSocket, WebSocketDisconnect, APIRouter, Depends, UploadFile
from typing import List
from database.session import db
from bson import ObjectId
from utils.connection_manager import manager




router = APIRouter()

# Store active WebSocket connections
active_connections: List[WebSocket] = []


# WebSocket route for group chat
@router.websocket("/ws/group/{group_id}")
async def websocket_endpoint(websocket: WebSocket, group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})

    if not group:
        await websocket.send_text("Group not found")
        await websocket.close(code=1003)
        return

    if current_user["email"] not in group["members"]:
        await websocket.send_text("Access denied: You're not a member of this group")
        await websocket.close(code=1003)
        return

    await manager.connect(websocket)

    try:
        while True:
            # Receive message from WebSocket
            data = await websocket.receive_text()
            # Save the message to the database
            await insert_message(group_id, current_user["email"], data)

            # Notify other users in the group about the new message
            notification_content = f"{current_user['email']} sent a new message in group {group_id}"
            await create_notification(group_id=group_id, sender=current_user, content=notification_content)

            # Broadcast the message to all connected users
            await manager.broadcast(f"{current_user['email']} in group {group_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{current_user['email']} left group {group_id}.")


# @router.post("/send_message/{group_id}", response_model=dict)
# async def send_message(group_id: str, message: MessageCreate, current_user: dict = Depends(get_current_user)):
#     # Check if the group exists
#     group = await db["groups"].find_one({"_id": ObjectId(group_id)})
#     if not group:
#         raise HTTPException(status_code=404, detail="Group not found")

#     # Check if the user is a member of the group
#     if current_user["email"] not in group["members"]:
#         raise HTTPException(status_code=403, detail="You are not a member of this group")

#       # Create a new message
#     message_in_db = MessageInDB(
#         group_id=group_id,
#         sender_email=current_user["email"],
#         content=message.content,
#         timestamp=datetime.utcnow()
#     )

#     # Save the message
#     await insert_message(message_in_db)

#     return {"message": "Message sent successfully"}

# Get all messages for a group
@router.get("/{group_id}", response_model=dict)
async def get_group_messages(group_id: str, current_user: dict = Depends(get_current_user)):
    group = await db["groups"].find_one({"_id": ObjectId(group_id)})

    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if the user is a member of the group
    if current_user["email"] not in group["members"]:
        raise HTTPException(status_code=403, detail="You are not a member of this group")
    
    # Fetch all messages for the group
    messages = await db["messages"].find({"group_id": group_id}).sort("timestamp", 1).to_list(100)
    
    # Convert ObjectId fields to strings
    for message in messages:
        message["_id"] = str(message["_id"])
        message["group_id"] = str(message["group_id"])
        message["timestamp"] = str(message["timestamp"])  # Optionally format this
    
    return {"messages": messages}

