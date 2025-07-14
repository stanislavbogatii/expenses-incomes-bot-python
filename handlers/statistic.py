from form import Form
from repositories import TransactionRepository, CategoryRepository
from aiogram import F, Router
from aiogram.filters.command import Command, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from utils import get_or_create_user
from datetime import datetime, timedelta
from models import UserModel
from enums import TransactionType
from keyboards.keyboards import get_statistic_options_inline, get_back_to_stats_inline, get_main_menu
from dateutil.relativedelta import relativedelta
from collections import defaultdict


transaction_repository = TransactionRepository()
category_repository = CategoryRepository()
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
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=now)
    
    
    lines = ['Transactions:']
    income_categories = defaultdict(float)
    expense_categories = defaultdict(float)

    for transaction in transactions:
        text = (
            f"{transaction.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"{transaction.type.value}: {transaction.amount:.2f} {transaction.currency}\n"
            f"Category: {transaction.category}"
        )
        lines.append(text)

        if transaction.type == TransactionType.INCOME:
            income_categories[transaction.category] += transaction.amount
        elif transaction.type == TransactionType.EXPENSE:
            expense_categories[transaction.category] += transaction.amount

    text = '\n\n'.join(lines)

    income_sum = sum(income_categories.values())
    expense_sum = sum(expense_categories.values())
    profit = income_sum - expense_sum

    income_lines = ['\n\n📈 Income by category: \n']
    for category, amount in income_categories.items():
        category_label = category_repository.get_category_label('income', category)
        income_lines.append(f"• {category_label}: {amount:.2f} {transaction.currency} \n")

    expense_lines = ['\n\n📉 Expense by category: \n']
    for category, amount in expense_categories.items():
        category_label = category_repository.get_category_label('expense', category)
        expense_lines.append(f"• {category_label}: {amount:.2f} {transaction.currency} \n")

    await message.edit_text(
        f"{start_date.strftime('%d.%m.%Y %H:%M')} - {now.strftime('%d.%m.%Y %H:%M')} statistic:\n\n"
        f"➖ Expense: {expense_sum:.2f} {transaction.currency}\n"
        f"➕ Income: {income_sum:.2f} {transaction.currency}\n\n"
        f"📊 Profit: {profit:.2f} {transaction.currency} {'😔' if profit < 0 else '👍'}"
        + ''.join(income_lines)
        + ''.join(expense_lines),
        reply_markup=get_back_to_stats_inline()
    )


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
    
    transactions = await transaction_repository.find_all_by_interval(user_id=user.id, start_date=start_date, end_date=end_date)

    lines = ['Transactions:']
    income_categories = defaultdict(float)
    expense_categories = defaultdict(float)

    for transaction in transactions:
        text = (
            f"{transaction.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"{transaction.type.value}: {transaction.amount:.2f} {transaction.currency}\n"
            f"Category: {transaction.category}"
        )
        lines.append(text)

        if transaction.type == TransactionType.INCOME:
            income_categories[transaction.category] += transaction.amount
        elif transaction.type == TransactionType.EXPENSE:
            expense_categories[transaction.category] += transaction.amount

    text = '\n\n'.join(lines)

    income_sum = sum(income_categories.values())
    expense_sum = sum(expense_categories.values())
    profit = income_sum - expense_sum

    income_lines = ['\n\n📈 Income by category: \n']
    for category, amount in income_categories.items():
        category_label = category_repository.get_category_label('income', category)
        income_lines.append(f"• {category_label}: {amount:.2f} {transaction.currency} \n")

    expense_lines = ['\n\n📉 Expense by category: \n']
    for category, amount in expense_categories.items():
        category_label = category_repository.get_category_label('expense', category)
        expense_lines.append(f"• {category_label}: {amount:.2f} {transaction.currency} \n")

    await message.edit_text(
        f"{start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')} statistic:\n\n"
        f"➖ Expense: {expense_sum:.2f} {transaction.currency}\n"
        f"➕ Income: {income_sum:.2f} {transaction.currency}\n\n"
        f"📊 Profit: {profit:.2f} {transaction.currency} {'😔' if profit < 0 else '👍'}"
        + ''.join(income_lines)
        + ''.join(expense_lines),
        reply_markup=get_back_to_stats_inline()
    )
