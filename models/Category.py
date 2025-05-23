from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from .PyObjectId import PyObjectId
from bson import ObjectId
from enums import TransactionType

class CategoryModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    title: str
    created_at: datetime
    updated_at: datetime

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
