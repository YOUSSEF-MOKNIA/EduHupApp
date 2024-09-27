from utils.s3 import update_profile_picture_in_s3
from routes.auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer
from utils.psw import hash_password, verify_password
from schemas.user import UserUpdate, UserUpdatePassword
from crud.user import update_user, get_user_by_email, update_user_password, delete_user_func
import os

# JWT Secret and Algorithm from environment variables
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme for the token endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Initialize router
router = APIRouter()

# Protected route example (only accessible to authenticated users)
@router.get("/me", response_model=dict)
async def get_user(current_user: dict = Depends(get_current_user)):
    return current_user

# delete account endpoint and remove it from group and repo and delete it's profile picture from s3
@router.delete("/delete_account", response_model=dict)
async def delete_user(current_user: dict = Depends(get_current_user)):
    if await delete_user_func(current_user):
        return {"message": "User deleted successfully"}


# User update profile endpoint 
@router.put("/update", response_model=dict)
async def update_user_profile(user: UserUpdate, current_user: dict = Depends(get_current_user)):
    # Update user details
    user_data = user.dict(exclude_unset=True)
    # exclude_unset=True will exclude any fields that are not set in the UserBase model
    update_result = await update_user(current_user["id"], user_data)
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")
    
    return {"message": "User updated successfully"}

# User update profile picture endpoint
@router.put("/update_picture", response_model=dict)
async def update_user_picture(new_pfp: UploadFile, current_user: dict = Depends(get_current_user)):
    # Upload the new profile picture to S3
    profile_picture_url = await update_profile_picture_in_s3(new_pfp, current_user["email"])
    
    # Update the user's profile picture URL
    update_result = await update_user(current_user["id"], {"profile_picture_url": profile_picture_url})
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")
    
    return {"message": "Profile picture updated successfully"}

# Update password endpoint
@router.put("/update_password", response_model=dict)
async def update_password(user_update: UserUpdatePassword, current_user: dict = Depends(get_current_user)):
    # Verify the old password
    user = await get_user_by_email(current_user["email"])
    if not user or not verify_password(user_update.old_password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    # Hash the new password
    hashed_new_password = hash_password(user_update.new_password)
    
    # Update the user's password
    update_result = await update_user_password(current_user["id"], hashed_new_password)
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")
    
    return {"message": "Password updated successfully"}
