from repositories import TransactionRepository
from aiogram import Router
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from utils import get_or_create_user
from datetime import datetime, timedelta
from keyboards import main_menu
from models import UserModel
from enums import TransactionType

transaction_repository = TransactionRepository()
router = Router()

@router.message(Command(commands=['statistic']))
async def cmd_get_statistic(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
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

    income_sum = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    expense_sum = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
    profit = income_sum - expense_sum

    await message.answer(
        f"{days} day statistic: \n\n" \
        f"Expense: {expense_sum} mdl\n" \
        f"Income: {income_sum} mdl\n\n" \
        f"Profit: {profit} mdl {'😔' if profit < 0 else '👍'}",
        reply_markup=main_menu,
    )
    await state.clear()

