from typing import List
from form import Form
from repositories import TransactionRepository, CategoryRepository, CurrencyRepository
from aiogram import F, Router
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from utils import get_or_create_user
from datetime import datetime, timedelta
from models import UserModel, TransactionModel
from enums import TransactionType
from keyboards.keyboards import get_statistic_options_inline, get_back_to_stats_inline, get_main_menu
from dateutil.relativedelta import relativedelta
from collections import defaultdict

transaction_repository = TransactionRepository()
category_repository = CategoryRepository()
currency_repository = CurrencyRepository()
router = Router()

stats_period_days = {
    "day": relativedelta(days=1),
    "week": relativedelta(weeks=1),
    "month": relativedelta(months=1),
    "three_months": relativedelta(months=3),
    "six_months": relativedelta(months=6),
    "year": relativedelta(years=1),
    "all": None,
    "custom": None,
}


# handlers
@router.message(Command(commands=['statistic', 'statistics', 'stat', 'stats']))
@router.message(lambda message: message.text.lower() in ['statistic', 'statistics', 'stat', 'stats'])
async def cmd_get_statistic(message: Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "Select interval for stats:",
        reply_markup=get_statistic_options_inline()
    )

@router.callback_query(F.data == 'show_stats')
async def cmd_add_expense(callback: CallbackQuery):
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
async def process_period(callback: CallbackQuery, state: FSMContext):
    message = callback.message
    period = callback.data.replace('stats_period_', '')
    if (period == 'custom'):
        await callback.message.edit_text(
            "Send me start date in format dd.mm.yyyy and end date in format dd.mm.yyyy, separated by space.\nExample: 01.01.2023 31.12.2023",
            reply_markup=get_back_to_stats_inline()
        )
        await state.set_state(Form.waiting_for_custom_stats_period)
        await callback.answer()
        return
    
    stats_period = stats_period_days[period]

    id = callback.from_user.id
    username = callback.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)

    now = datetime.now()

    if stats_period is None:
        start_date = datetime.min 
    else:
        start_date = now - stats_period

    await state.update_data(start_date=start_date, end_date=now)
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=now)
    text = create_stats_message(start_date, now, transactions)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Convert to one currency', callback_data='convert_stats')],
            [InlineKeyboardButton(text='<< BACK', callback_data='show_stats')],
        ]
    )
    await message.edit_text(text, reply_markup=keyboard)


@router.message(Form.waiting_for_custom_stats_period)
async def get_statistic_for_custom_period(message: Message, state: FSMContext):
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
    
    state.update_data(start_date=start_date, end_date=end_date)
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=end_date)
    text = create_stats_message(start_date, end_date, transactions)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Convert to one currency', callback_data='convert_stats')],
            [InlineKeyboardButton(text='<< BACK', callback_data='show_stats')],
        ]
    )
    await message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data == 'convert_stats')
async def process_period(callback: CallbackQuery, state: FSMContext):
    keyboard: InlineKeyboardMarkup = await create_currencies_buttons_list()
    message = callback.message
    await message.answer("Select currency", reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data.startswith('show_converted_stats_currency:'))
async def cmd_show_currencies_for_source(callback: CallbackQuery, state: FSMContext):
    currency_code = callback.data.split("show_converted_stats_currency:")[1]
    data = await state.get_data()
    message = callback.message
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    username = callback.from_user.username
    user_id = callback.from_user.id
    user: UserModel = await get_or_create_user(username=username, user_id=user_id)
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=end_date)
    text = await create_one_amount_stats_message(start_date, end_date, transactions, currency_code)
    await message.edit_text(text, reply_markup=get_back_to_stats_inline())
    await state.clear()
    await callback.answer()
    



# functions
def create_stats_message(start_date: datetime, end_date: datetime, transactions) -> str:
    income_by_currency = defaultdict(lambda: defaultdict(float))
    expense_by_currency = defaultdict(lambda: defaultdict(float))

    for transaction in transactions:
        if transaction.type == TransactionType.INCOME:
            income_by_currency[transaction.currency][transaction.category] += transaction.amount
        elif transaction.type == TransactionType.EXPENSE:
            expense_by_currency[transaction.currency][transaction.category] += transaction.amount


    text = (
        f"{start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')} statistic:\n\n"
    )
    currencies = set(income_by_currency.keys()) | set(expense_by_currency.keys())

    for currency in currencies:
        income_categories = income_by_currency.get(currency, {})
        expense_categories = expense_by_currency.get(currency, {})
        income_sum = sum(income_categories.values())
        expense_sum = sum(expense_categories.values())
        profit = income_sum - expense_sum

        text += (
            f"\n===========Currency: {currency.upper()}===========\n"
            f"➖ Expense: {expense_sum:.2f} {currency}\n"
            f"➕ Income: {income_sum:.2f} {currency}\n"
            f"📊 Profit: {profit:.2f} {currency} {'😔' if profit < 0 else '👍'}\n"
        )

        if income_categories:
            text += '\n📈 Income by category:\n'
            for category, amount in income_categories.items():
                label = category_repository.get_category_label('income', category)
                text += f"• {label}: {amount:.2f} {currency}\n"

        if expense_categories:
            text += '\n📉 Expense by category:\n'
            for category, amount in expense_categories.items():
                label = category_repository.get_category_label('expense', category)
                text += f"• {label}: {amount:.2f} {currency}\n"
    return text

async def create_one_amount_stats_message(start_date: datetime, end_date: datetime, transactions: List[TransactionModel], currency: str) -> str:
    income_categories = defaultdict(float)
    expense_categories = defaultdict(float)

    for transaction in transactions:
        amount = transaction.amount
        if transaction.currency != currency:
            amount = await currency_repository.get_currency(transaction.currency, currency) * amount

        if transaction.type == TransactionType.INCOME:
            income_categories[transaction.category] += amount
        elif transaction.type == TransactionType.EXPENSE:
            expense_categories[transaction.category] += amount


    income_sum = sum(income_categories.values())
    expense_sum = sum(expense_categories.values())
    profit = income_sum - expense_sum

    income_lines = ['\n\n📈 Income by category: \n']
    for category, amount in income_categories.items():
        category_label = category_repository.get_category_label('income', category)
        income_lines.append(f"• {category_label}: {amount:.2f} {currency} \n")

    expense_lines = ['\n\n📉 Expense by category: \n']
    for category, amount in expense_categories.items():
        category_label = category_repository.get_category_label('expense', category)
        expense_lines.append(f"• {category_label}: {amount:.2f} {currency} \n")
    text = (
        f"{start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')} statistic:\n\n"
        f"➖ Expense: {expense_sum:.2f} {currency}\n"
        f"➕ Income: {income_sum:.2f} {currency}\n\n"
        f"📊 Profit: {profit:.2f} {currency} {'😔' if profit < 0 else '👍'}"
        + ''.join(income_lines)
        + ''.join(expense_lines)
    )
    return text


async def create_currencies_buttons_list() -> InlineKeyboardMarkup:
    currencies = await currency_repository.find_all()
    buttons = []
    for currency in currencies:
        buttons.append([InlineKeyboardButton(text=f"({currency.code}) {currency.label} {currency.symbol}", callback_data=f"show_converted_stats_currency:{currency.code}")])
    buttons.append([
        InlineKeyboardButton(text='<< BACK', callback_data='show_stats'),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
