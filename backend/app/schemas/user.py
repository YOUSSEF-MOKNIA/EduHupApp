from pydantic import BaseModel, EmailStr
from typing import Optional, Union
from fastapi import UploadFile

# Base model for user input
class UserBase(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: EmailStr

class UserUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    username: Optional[str] = None
    email: Optional[EmailStr] = None

class UserCreate(UserBase):
    password: str
    
class UserResponse(UserBase):
    id: Optional[str]  # MongoDB's _id, but stringified
    is_active: bool
    profile_picture_url: Optional[str] = None  # Store profile picture URL

# Schema for updating user password
class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str

# User login schema
class UserLogin(BaseModel):
    identifier: Union[EmailStr, str]
    password: str

# Model for token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Model for token data (used for extracting user details from the token)
class TokenData(BaseModel):
    id: Optional[str] = None
