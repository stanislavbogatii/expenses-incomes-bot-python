from db.mongo import db
from models import TransactionModel
from typing import List
from models import PyObjectId

class TransactionRepository:
    def __init__(self):
        self.transactions = db['transactions']

    async def find_one_by_id(self, id: str) -> TransactionModel | None:
        transaction = await self.transactions.find_one({"id": id})
        if transaction:
            return TransactionModel(**transaction)
        return None
    
    async def find_all_by_user_id(self, user_id: PyObjectId) -> List[TransactionModel]:
        data_list = await self.transactions.find({"user_id": user_id}).to_list(length=None)

        transactions = [
            TransactionModel(**{**data})
            for data in data_list
        ]
        return transactions

    async def store(self, transaction: TransactionModel) -> TransactionModel:
        transaction = await self.transactions.insert_one(transaction.dict(by_alias=True))
        return transaction