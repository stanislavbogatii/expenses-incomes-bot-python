from config import config
from commands import get_main_commands, get_admin_commands
import asyncio
from aiogram import F, Bot, Dispatcher
from handlers import register_all_handlers
from aiogram.types import BotCommandScopeDefault, BotCommandScopeChat

bot = Bot(token=config.bot_token.get_secret_value())
dp = Dispatcher()


async def set_commands(bot: Bot):
    await bot.set_my_commands(get_main_commands())
    for admin_id in config.admin_ids:
        await bot.set_my_commands(get_admin_commands(), scope=BotCommandScopeChat(chat_id=admin_id))

async def main():
    register_all_handlers(dp)
    await set_commands(bot)
    await dp.start_polling(bot)

if __name__ == "__main__":
    print('Running')
    asyncio.run(main())