from db.mongo import db
from models import CurrencyModel
from typing import List
from datetime import datetime, timedelta
from models import PyObjectId
from pymongo import ReturnDocument


class CurrencyRepository:
    def __init__(self):
        self.currencies = db['currencies']

    async def find_one_by_id(self, id: str) -> CurrencyModel | None:
        currency = await self.currencies.find_one({"_id": PyObjectId(id)})
        if currency:
            return CurrencyModel(**currency)
        return None
    
    async def find_one_by_code(self, code: str) -> CurrencyModel | None:
        currency = await self.currencies.find_one({"code": code})
        if currency:
            return CurrencyModel(**currency)
        return None
    
    async def delete_one_by_id(self, id: str):
        await self.currencies.delete_one({"_id": PyObjectId(id)})
        return None


    async def get_currency(self, from_currency: str, to_currency: str) -> float:
        currency = await self.find_one_by_code(from_currency)
        if currency is None: 
            return
        
        if currency.rates is None:
            currency = await self.update_currency_rates(from_currency)
        
        rates_dict = dict(rate.split(": ") for rate in currency.rates)

        if rates_dict is None or not rates_dict:
            currency = await self.update_currency_rates(from_currency)
            rates_dict = dict(rate.split(": ") for rate in currency.rates)

        rate = rates_dict[f"{from_currency}{to_currency}"]

        if rate is None:
            currency = await self.update_currency_rates(from_currency)
            rates_dict = dict(rate.split(": ") for rate in currency.rates)
            rate = rates_dict[f"{from_currency}{to_currency}"]

        active = datetime.utcnow() - currency.updated_at < timedelta(days=1)
        
        if active is False:
            currency = await self.update_currency_rates(from_currency)
            rates_dict = dict(rate.split(": ") for rate in currency.rates)
            rate = rates_dict[f"{from_currency}{to_currency}"]
        
        if rate is None:
            raise ValueError(f"Currency rate for {from_currency}{to_currency} not found")

        rate = float(rate)
        return rate
    
    async def update_currency_rates(self, currency: str):
        from services import CurrencyExchangeService

        quotes = await CurrencyExchangeService.get_currencies_by_source(currency)
        rates = [f"{code}: {rate}" for code, rate in quotes.items()]
        update_data = {
            "rates": rates,
            "updated_at": datetime.now()
        }
        updated_currency = await self.currencies.find_one_and_update(
            {"code": currency},
            {"$set": update_data},
            return_document=ReturnDocument.AFTER 
        )

        if updated_currency:
            return CurrencyModel(**updated_currency)
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
