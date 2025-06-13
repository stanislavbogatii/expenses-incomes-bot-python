from aiogram.types import BotCommand   

def get_main_commands()->list[BotCommand]:
    main_commands = [
        BotCommand(command="/start", description="Start bot"),
        BotCommand(command="/menu", description="Menu"),
        BotCommand(command="/transactions", description="Transaction"),
        BotCommand(command="/statistic", description="Statistic"),
        BotCommand(command="/help", description="Help"),
        BotCommand(command="/add_income", description="Add income"),
        BotCommand(command="/add_expense", description="Add expense"),
        BotCommand(command="/profile", description="Profile"),
    ]   
    return main_commands

def get_admin_commands() -> list[BotCommand]:
    main_commands = get_main_commands()
    main_commands.append(BotCommand(command="/users", description="Users"))
    # main_commands.append(BotCommand(command="/categories", description="Categories"))
    # main_commands.append(BotCommand(command="/create_category", description="Create category"))
    return main_commands
