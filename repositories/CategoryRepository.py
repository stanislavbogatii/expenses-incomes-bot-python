from db.mongo import db
from models import CategoryModel
from typing import List
from enums import CategoryType

class CategoryRepository:
    def __init__(self):
        self.categories = db['categories']
    
    async def find_all(self) -> List[CategoryModel]:
        data_list = await self.categories.find().to_list(length=None)
        categories = [
            CategoryModel(**{**data})
            for data in data_list
        ]
        return categories
    
    async def find_all_by_type(self, type: CategoryType) -> List[CategoryModel]:
        data_list = await self.categories.find({"type": type}).to_list(length=None)
        categories = [
            CategoryModel(**{**data})
            for data in data_list
        ]
        return categories
    
    async def store(self, category: CategoryModel)->CategoryModel:
        category = await self.categories.insert_one(category.dict(by_alias=True))
        return category
