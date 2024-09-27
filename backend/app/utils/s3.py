from fastapi import UploadFile
import boto3
from botocore.exceptions import NoCredentialsError
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get MongoDB connection string from environment variables
BUCKET_NAME = os.getenv("FILES_BUCKET_NAME")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")


# Initialize S3 client with your AWS credentials
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION_NAME
)

# Upload file to S3
async def upload_file_to_s3(file: UploadFile):
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, f"Repo_Documents/{file.filename}")
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/Repo_Documents/{file.filename}"
        return file_url
    except NoCredentialsError:
        raise Exception("Credentials not available")
    
# Get file from S3
async def get_file_from_s3(filename: str):
    try:
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/Repo_Documents/{filename}"
        return file_url
    except NoCredentialsError:
        raise Exception("Credentials not available")
    
# Delete file from S3
async def delete_file_from_s3(filename: str):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=f"Repo_Documents/{filename}")
    except NoCredentialsError:
        raise Exception("Credentials not available")
    
# Add group file to S3
async def upload_group_file_to_s3(file: UploadFile):
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, f"Group_Documents/{file.filename}")
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/Group_Documents/{file.filename}"
        return file_url
    except NoCredentialsError:
        raise Exception("Credentials not available")

# Get all group files from S3
async def get_group_files_from_s3(group_files: list):
    try:
        files = []
        for file in group_files:
            file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/Group_Documents/{file['filename']}"
            files.append({"filename": file["filename"], "url": file_url})
        return files
    except NoCredentialsError:
        raise Exception("Credentials not available")
    
# Delete group file from S3
async def delete_group_file_from_s3(filename: str):
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=f"Group_Documents/{filename}")
    except NoCredentialsError:
        raise Exception("Credentials not available")
    

# Add profile picture to S3
async def upload_profile_picture_to_s3(file: UploadFile, email: str):
    try:
        s3_client.upload_fileobj(file.file, BUCKET_NAME, f"profile_pictures/{email}")
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/profile_pictures/{email}"
        return file_url
    except NoCredentialsError:
        raise Exception("Credentials not available")
    
# update profile picture in S3
async def update_profile_picture_in_s3(file: UploadFile, email: str):
    try:
        # Delete the old profile picture from S3 and upload the new one
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=f"profile_pictures/{email}")
        s3_client.upload_fileobj(file.file, BUCKET_NAME, f"profile_pictures/{email}")
        # take the file name without extension example: file.txt -> file
        name = file.filename.split(".")[0]
        file_key = f"{email}&{name}"
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/profile_pictures/{file_key}"
        return file_url
    except NoCredentialsError:
        raise Exception("Credentials not available")
    
# Get profile picture from S3
async def get_profile_picture_from_s3(email: str):
    try:
        file_url = f"https://{BUCKET_NAME}.s3.{AWS_REGION_NAME}.amazonaws.com/profile_pictures/{email}"
        return file_url
    except NoCredentialsError:
        raise Exception("Credentials not available")

# Delete profile pic from S3
async def delete_profile_picture_from_s3(current_user: dict):
    try:
        # Delete user's profile picture from S3
        if current_user.get("profile_picture_url"):
            file_key = current_user["email"]
            s3_client.delete_object(Bucket=BUCKET_NAME, Key=f"profile_pictures/{file_key}")
    except NoCredentialsError:
        raise Exception("Credentials not available")
