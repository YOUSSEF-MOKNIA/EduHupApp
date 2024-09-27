from utils.s3 import upload_profile_picture_to_s3
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from models.user import UserInDB, user_db_to_response
from utils.psw import hash_password, verify_password
from schemas.user import UserCreate, Token, TokenData, UserLogin
from database.session import db  # Import the MongoDB connection from session.py
from typing import Optional
import os
from bson import ObjectId
from pydantic import EmailStr


# JWT Secret and Algorithm from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for the token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Initialize router
router = APIRouter()

# Helper function to create JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Dependency to convert form data to UserCreate schema
def get_user_create(
    firstname: str = Form(...),
    lastname: str = Form(...),
    username: str = Form(...),
    email: EmailStr = Form(...),
    password: str = Form(...)
) -> UserCreate:
    return UserCreate(firstname=firstname, lastname=lastname, username=username, email=email, password=password)

@router.post("/register", response_model=dict)
async def register_user(
    user: UserCreate = Depends(get_user_create),  # Use form data to create UserCreate schema
    profile_picture: Optional[UploadFile] = File(None)  # Optional profile picture
):
    # Check if the user already exists
    existing_user = await db["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash the user's password
    hashed_password = hash_password(user.password)

    # Initialize the profile picture URL as None
    profile_picture_url = None

    # If a profile picture is uploaded, upload it to S3 and get the file URL
    if profile_picture:
        profile_picture_url = await upload_profile_picture_to_s3(profile_picture, user.email)

    # Create a UserInDB instance with the profile picture URL (if any)
    user_in_db = UserInDB(
        firstname=user.firstname,
        lastname=user.lastname,
        username=user.username,
        email=user.email,
        password=hashed_password,  # Store the hashed password
        profile_picture_url=profile_picture_url  # Could be None if not uploaded
    )

    # Save the user to the database
    new_user = await db["users"].insert_one(user_in_db.dict())

    return {"message": "User registered successfully", "user_id": str(new_user.inserted_id)}

# User login endpoint (Token generation)
@router.post("/login", response_model=Token) 
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
     # Try to find the user by email or username
    user = await db["users"].find_one({
        "$or": [
            # {"email": form_data.identifier},  # If identifier is email
            {"username": form_data.username}  # If identifier is username
        ]
    })
    
    # If user not found or password is incorrect, raise an exception
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=400, detail="Incorrect Email/Username or Password")

    
    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"id": str(user["_id"])}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


# it will check if the token is valid or not and return the user details
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        verify_jwt_token(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(id=user_id)
    except JWTError:
        raise credentials_exception

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    return user_db_to_response(user)


# Logout functionality
# Simulated token blacklist (you can replace this with a Redis store)
TOKEN_BLACKLIST = set()

# Function to blacklist token
def blacklist_token(token: str):
    TOKEN_BLACKLIST.add(token)

# Verify if token is in the blacklist
def is_token_blacklisted(token: str):
    return token in TOKEN_BLACKLIST

# Logout endpoint
@router.post("/auth/logout", response_model=dict)
async def logout_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=400, detail="No token provided")

    # Add token to blacklist
    blacklist_token(token)

    return {"message": "Logged out successfully"}

# You would also need to check blacklisted tokens when validating JWTs
def verify_jwt_token(token: str):
    if is_token_blacklisted(token):
        raise HTTPException(status_code=401, detail="You are not authorized to perform this action! Please log in again.")
