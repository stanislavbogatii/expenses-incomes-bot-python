from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from repositories import UserRepository

router = Router()
user_repository = UserRepository()

@router.message(Command(commands=['users']))
@router.message(lambda message: message.text.lower() in ['users'])
async def cmd_get_users(message: Message):
    users = await user_repository.find_all()
    lines = [f'Current users: ({len(users)})\n']
    for user in users:
        lines.append(f"{user.username}  -  {user.created_at.strftime('%d.%m.%Y')}\nid: {user.user_id}\n") 
    text = '\n'.join(lines)

    await message.answer(text)