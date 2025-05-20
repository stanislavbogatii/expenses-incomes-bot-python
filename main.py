from config import config
from commands import main_commands
import asyncio
from aiogram import F, Bot, Dispatcher
from handlers import register_all_handlers



bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()

async def set_commands(bot: Bot):
    await bot.set_my_commands(main_commands)

async def main():
    register_all_handlers(dp)
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())