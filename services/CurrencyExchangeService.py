from config import config
import aiohttp

from repositories import CurrencyRepository

currency_repository = CurrencyRepository()

class CurrencyExchangeService:
    BASE_URL = "https://api.exchangerate.host/"
    currency_repository = CurrencyRepository()

    @staticmethod
    async def get_currencies_by_source(source_code: str) -> float:
        
        source_model = await CurrencyExchangeService.currency_repository.find_one_by_code(source_code)
        if (source_model is None):
            return None
        
        currencies = await CurrencyExchangeService.currency_repository.find_all()
        codes = [c.code for c in currencies]
        codes = ",".join(codes)

        url = f"{CurrencyExchangeService.BASE_URL}live?access_key={config.exchangerate_api_key}&source={source_code}&currencies={codes}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data['quotes']
                
    
