from datetime import datetime
from http.client import HTTPException
from models.messages import MessageInDB
from database.session import db  # Import the database connection


async def insert_message(message: MessageInDB):
    new_message = await db["messages"].insert_one(message)
    if new_message:
        return {"message": "Message sent successfully", "id": str(new_message.inserted_id)}
    else:
        raise HTTPException(status_code=400, detail="Failed to create the message")