from aiogram.types import BotCommand   

main_commands = [
    BotCommand(command="/start", description="Start bot"),
    BotCommand(command="/transactions", description="Transaction"),
    BotCommand(command="/help", description="Help"),
    BotCommand(command="/add_income", description="Add income"),
    BotCommand(command="/add_expense", description="Add expense"),
    BotCommand(command="/profile", description="Profile"),
]