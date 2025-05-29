
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from form import Form
from models import UserModel
from keyboards import get_main_menu, get_transacion_options_inline, get_back_to_transactions_inline
from repositories import UserRepository, TransactionRepository
from utils import get_or_create_user
from dateutil.relativedelta import relativedelta

user_repository = UserRepository()
transaction_repository = TransactionRepository()

router = Router()

transactions_period_days = {
    "day": relativedelta(days=1),
    "week": relativedelta(weeks=1),
    "month": relativedelta(months=1),
    "three_months": relativedelta(months=3),
    "six_months": relativedelta(months=6),
    "year": relativedelta(years=1),
    "all": None,
    "custom": None,
}

@router.message(Command(commands=['transactions']))
async def cmd_get_transactions(message: Message, command: CommandObject, state: FSMContext):
    await state.clear()
    await message.answer(
        "Select interval for transactions:",
        reply_markup=get_transacion_options_inline()
    )



@router.message(Form.waiting_for_custom_transactions_period)
async def cmd_waiting_for_income(message: Message, state: FSMContext):
    start_date_str, end_date_str = message.text.split()
    await state.clear()
    username = message.from_user.username
    user_id = message.from_user.id
    user: UserModel = await get_or_create_user(username=username, user_id=user_id)
    if len(start_date_str) != 10 or len(end_date_str) != 10:
        await message.answer(
            "Invalid date format. Please, send me start date in format dd.mm.yyyy and end date in format dd.mm.yyyy, separated by space.\nExample: 01.01.2023 31.12.2023",
        )
        return
    try:
        start_date = datetime.strptime(start_date_str, '%d.%m.%Y')
        end_date = datetime.strptime(end_date_str, '%d.%m.%Y')
    except ValueError:
        await message.answer(
            "Invalid date format. Please, send me start date in format dd.mm.yyyy and end date in format dd.mm.yyyy, separated by space.\nExample: 01.01.2023 31.12.2023",
        )
        return
    if start_date > end_date:
        await message.answer(
            "Start date cannot be later than end date. Please, send me start date in format dd.mm.yyyy and end date in format dd.mm.yyyy, separated by space.\nExample: 01.01.2023 31.12.2023",
        )
        return
    
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=end_date)

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
        reply_markup=get_back_to_transactions_inline()
    )


@router.callback_query(F.data.startswith('transactions_period_'))
async def process_period(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    period = callback.data.replace('transactions_period_', '')
    if (period == 'custom'):
        await state.set_state(Form.waiting_for_custom_transactions_period)
        await callback.message.edit_text(
            "Please, send me start date in format dd.mm.yyyy and end date in format dd.mm.yyyy, separated by space.\nExample: 01.01.2023 31.12.2023",
        )
        await callback.answer()
        return
    stats_period = transactions_period_days[period]

    id = callback.from_user.id
    username = callback.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)

    now = datetime.now()

    if stats_period is None:
        start_date = datetime.min 
    else:
        start_date = now - stats_period
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=now)

    lines = ['Transactions:']
    for transaction in transactions:
        text = (
            f"{transaction.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"{transaction.type.value}: {transaction.amount:.2f} mdl"
        )
        lines.append(text)

    text = '\n\n'.join(lines)

    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_transactions_inline()
    )
    await callback.answer()


@router.callback_query(F.data == 'show_transactions')
async def cmd_add_expense(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    id = message.from_user.id
    username = message.from_user.username
    await get_or_create_user(username=username, user_id=id)
        
    await callback.message.edit_text(
        "Select interval for transactions:",
        reply_markup=get_transacion_options_inline()
    )
    await callback.answer()
