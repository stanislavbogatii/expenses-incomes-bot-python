
from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from form import Form
from models import UserModel, TransactionModel
from keyboards.keyboards import get_main_menu, get_transacion_options_inline, get_back_to_transactions_inline
from repositories import UserRepository, TransactionRepository, CategoryRepository
from utils import get_or_create_user
from dateutil.relativedelta import relativedelta
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from enums import TransactionType

user_repository = UserRepository()
transaction_repository = TransactionRepository()
category_repository = CategoryRepository()

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
@router.message(lambda message: message.text.lower() in ['transactions'])
async def cmd_get_transactions(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Select interval for transactions:",
        reply_markup=get_transacion_options_inline()
    )

@router.message(Form.waiting_for_custom_transactions_period)
async def cmd_show_transactions(message: Message, state: FSMContext):
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
    
    transactions: list[TransactionModel] = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=end_date)
    keyboard = create_transactions_list(transactions)

    await message.answer(
        "Transactions:",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith('transactions_period_'))
async def process_period(callback: CallbackQuery, state: FSMContext):
    period = callback.data.replace('transactions_period_', '')
    if (period == 'custom'):
        await state.set_state(Form.waiting_for_custom_transactions_period)
        await callback.message.edit_text(
            "Please, send me start date in format dd.mm.yyyy and end date in format dd.mm.yyyy, separated by space.\nExample: 01.01.2023 31.12.2023",
        )
        await callback.answer()
        return
    transactions_period = transactions_period_days[period]
    id = callback.from_user.id
    username = callback.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)
    now = datetime.now()
    if transactions_period is None:
        start_date = datetime.min 
    else:
        start_date = now - transactions_period
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=now)
    keyboard = create_transactions_list(transactions)
    await callback.message.edit_text(
        "Transactions:",
        reply_markup=keyboard
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


@router.callback_query(F.data == 'empty')
async def cmd_empty(callback: CallbackQuery, state: FSMContext):
    await callback.answer()




def create_transactions_list(transactions: list [TransactionModel]) -> InlineKeyboardMarkup:
    buttons = []
    prev_day = None
    for transaction in transactions:
        day = transaction.created_at.strftime('%d.%m.%Y')
        if (prev_day != day): 
            buttons.append([InlineKeyboardButton(text=f"============{day}============", callback_data="empty")])
        prev_day = day
        transactoin_emoji = transaction.type.value == TransactionType.INCOME.value and '➕' or '➖'
        buttons.append([
            InlineKeyboardButton(text=(
            f"{transactoin_emoji} {transaction.amount:.2f} mdl     |     {category_repository.get_category_label(transaction.type.value, transaction.category)}"
            ), callback_data=f"open_transaction_{transaction.id}")
        ])

    buttons.append([
        InlineKeyboardButton(text='<< BACK', callback_data='show_transactions'),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard