from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .PyObjectId import PyObjectId
from bson import ObjectId
from enums import TransactionType

# collection report_messgae_model

class ReportMessageModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        validate_by_name = True