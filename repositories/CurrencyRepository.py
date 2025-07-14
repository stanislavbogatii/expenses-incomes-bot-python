from db.mongo import db
from models import CurrencyModel
from typing import List
from models import PyObjectId

class CurrencyRepository:
    def __init__(self):
        self.currencies = db['currencies']

    async def find_one_by_id(self, id: str) -> CurrencyModel | None:
        currency = await self.currencies.find_one({"_id": PyObjectId(id)})
        if currency:
            return CurrencyModel(**currency)
        return None
    
    async def delete_one_by_id(self, id: str):
        await self.currencies.delete_one({"_id": PyObjectId(id)})
        return None
    
    
    async def find_all(self) -> List[CurrencyModel]:
        data_list = await self.currencies.find().to_list(length=None)

        currencies = [
            CurrencyModel(**{**data})
            for data in data_list
        ]
        return currencies

    async def store(self, currency: CurrencyModel) -> None:
        await self.currencies.insert_one(currency.dict(by_alias=True))
