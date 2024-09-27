from pydantic import BaseModel

class MessageCreate(BaseModel):
    content: str

# file upload schema
class SendFile(BaseModel):
    filename: str
    url: str