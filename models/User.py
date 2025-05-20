from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, Field
from .PyObjectId import PyObjectId
from datetime import datetime

# collection users

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    username: str
    user_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            ObjectId: str
        }
        validate_by_name = True