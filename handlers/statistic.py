from repositories import TransactionRepository
from aiogram import F, Router
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils import get_or_create_user
from datetime import datetime, timedelta
from models import UserModel
from enums import TransactionType
from keyboards import get_statistic_options_inline, get_back_to_stats_inline, get_main_menu
from dateutil.relativedelta import relativedelta


transaction_repository = TransactionRepository()
router = Router()

stats_period_days = {
    "day": relativedelta(days=1),
    "week": relativedelta(weeks=1),
    "month": relativedelta(months=1),
    "three_months": relativedelta(months=3),
    "six_months": relativedelta(months=6),
    "year": relativedelta(years=1),
    "all": None,
}

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

    now = datetime.now()
    start_date = now - relativedelta(days=int(days))


    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=now)

    income_sum = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    expense_sum = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
    profit = income_sum - expense_sum

    await message.answer(
        f"{days} day statistic: \n\n" \
        f"Expense: {expense_sum} mdl\n" \
        f"Income: {income_sum} mdl\n\n" \
        f"Profit: {profit} mdl {'😔' if profit < 0 else '👍'}",
        reply_markup=get_main_menu(),
    )

@router.callback_query(F.data == 'show_stats')
async def cmd_add_expense(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    id = message.from_user.id
    username = message.from_user.username
    await get_or_create_user(username=username, user_id=id)
        
    await callback.message.edit_text(
        "Select interval for stats:",
        reply_markup=get_statistic_options_inline()
    )
    await callback.answer()

@router.callback_query(F.data.startswith('stats_period_'))
async def process_period(callback: CallbackQuery):
    message = callback.message
    period = callback.data.replace('stats_period_', '')
    stats_period = stats_period_days[period]

    id = callback.from_user.id
    username = callback.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)

    now = datetime.now()

    if stats_period is None:
        start_date = datetime.min 
    else:
        start_date = now - stats_period
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=now)
    income_sum = sum(t.amount for t in transactions if t.type == TransactionType.INCOME)
    expense_sum = sum(t.amount for t in transactions if t.type == TransactionType.EXPENSE)
    profit = income_sum - expense_sum


    await callback.message.edit_text(
        f"{period} statistic: \n\n" \
        f"Expense: {expense_sum} mdl\n" \
        f"Income: {income_sum} mdl\n\n" \
        f"Profit: {profit} mdl {'😔' if profit < 0 else '👍'}",
        reply_markup=get_back_to_stats_inline()
    )
    await callback.answer()


