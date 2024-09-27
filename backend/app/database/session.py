from motor.motor_asyncio import AsyncIOMotorClient  # Motor is the async driver for MongoDB
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get MongoDB connection string from environment variables
MONGO_URL = os.getenv("MONGO_URL")

# Connect to MongoDB
client = AsyncIOMotorClient(MONGO_URL)
db = client["eduhub"]  # "eduhub" is the name of the database you want to use
