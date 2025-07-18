from config import config
import aiohttp
# Удали глобальный импорт:
# from repositories.CurrencyRepository import CurrencyRepository

class CurrencyExchangeService:
    BASE_URL = "https://api.exchangerate.host"

    @staticmethod
    async def get_currencies_by_source(source_code: str) -> float:
        from repositories.CurrencyRepository import CurrencyRepository  # <-- внутри метода
        currency_repository = CurrencyRepository()

        source_model = await currency_repository.find_one_by_code(source_code)
        if source_model is None:
            return None
        
        currencies = await currency_repository.find_all()
        codes = ",".join([c.code for c in currencies])

        url = f"{CurrencyExchangeService.BASE_URL}/live?access_key={config.exchangerate_api_key}&source={source_code}&currencies={codes}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data['quotes']

    @staticmethod
    async def convert(amount: int, from_currency: str, to_currency: str):
        url = f"{CurrencyExchangeService.BASE_URL}/convert?access_key={config.exchangerate_api_key}&from={from_currency}&to={to_currency}&amount={amount}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                print(response)
