from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, profile, group, repo, messages, notifications
from database.session import db  # Import the MongoDB connection

# Create FastAPI app instance
app = FastAPI()

# Set up CORS (Cross-Origin Resource Sharing)
# This is important if your frontend and backend are hosted on different domains
origins = [
    "http://localhost",  # Adjust this for your frontend URL if needed
    "http://localhost:3000"
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Include the authentication routes from auth.py
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(repo.router, prefix="/repo", tags=["Repo"])
app.include_router(group.router, prefix="/group", tags=["Group"])
app.include_router(messages.router, prefix="/messages", tags=["Messages"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])




# Root endpoint to check if the API is working
@app.get("/")
async def root():
    return {"message": "EduHub API is running!"}
