
from datetime import datetime, timedelta
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from form import Form
from models import UserModel
from keyboards import main_menu
from repositories import UserRepository, TransactionRepository
from utils import get_or_create_user

user_repository = UserRepository()
transaction_repository = TransactionRepository()

router = Router()

@router.message(Command(commands=['transactions']))
async def cmd_get_transactions(message: types.Message, command: CommandObject, state: FSMContext):
    await state.set_state(Form.waiting_for_income)
    days = command.args

    if not days or not days.isdigit():
        await message.answer("Not valid days number")
        return
    
    id = message.from_user.id
    username = message.from_user.username

    user: UserModel = await get_or_create_user(username=username, user_id=id)

    now = datetime.today()
    start_date = now - timedelta(days=int(days))
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=now)

    lines = ['Transactions:']
    for transaction in transactions:
        text = (
            f"{transaction.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"{transaction.type.value}: {transaction.amount:.2f} mdl"
        )
        lines.append(text)

    text = '\n\n'.join(lines)

    await message.answer(
        text,
        reply_markup=main_menu,
    )
    await state.clear()

