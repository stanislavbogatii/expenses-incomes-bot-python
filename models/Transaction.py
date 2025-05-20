from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .PyObjectId import PyObjectId
from bson import ObjectId
from enums import TransactionType

# collection transactions

class TransactionModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    type: TransactionType
    user_id: PyObjectId
    amount: float
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        validate_by_name = True

    def dict(self, **kwargs):
        data = super().dict(**kwargs)
        data['type'] = data['type'].value
        return data

