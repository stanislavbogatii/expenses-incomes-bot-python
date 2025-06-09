
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from form import Form
from models import UserModel
from keyboards import get_main_menu, get_transacion_options_inline, get_back_to_transactions_inline
from repositories import UserRepository, TransactionRepository, CategoryRepository
from utils import get_or_create_user
from dateutil.relativedelta import relativedelta
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from enums import CategoryType


router = Router()
transaction_repository = TransactionRepository()

@router.callback_query(F.data.startswith('open_transaction_'))
async def open_transaction(callback: CallbackQuery, state: FSMContext):
    id = callback.data.replace('open_transaction_', '')
    transaction = await transaction_repository.find_one_by_id(id)
    await callback.message.edit_text(
        f"{transaction.type.value} {transaction.created_at.strftime('%d.%m.%Y')} {transaction.amount:.2f} mdl ({transaction.category})",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='DELETE', callback_data='confirm_delete_transaction_'+id)],
                [InlineKeyboardButton(text='<< BACK', callback_data='show_transactions')]
            ]
        )
    )
    await callback.answer()

@router.callback_query(F.data.startswith('confirm_delete_transaction_'))
async def confirm_delete_transaction(callback: CallbackQuery, state: FSMContext):
    id = callback.data.replace('confirm_delete_transaction_', '')
    transaction = await transaction_repository.find_one_by_id(id)
    await callback.message.edit_text(
        f"Are you sure you want to delete {transaction.type.value} {transaction.created_at.strftime('%d.%m.%Y')} {transaction.amount:.2f} mdl ({transaction.category})?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='YES', callback_data='delete_transaction_'+id)],
                [InlineKeyboardButton(text='NO', callback_data='open_transaction_'+id)]
            ]
        )
    )
    await callback.answer()

@router.callback_query(F.data.startswith('delete_transaction_'))
async def confirm_delete_transaction(callback: CallbackQuery, state: FSMContext):
    id = callback.data.replace('delete_transaction_', '')
    await transaction_repository.delete_one_by_id(id)
    await callback.message.edit_text(
        f"Transaction success deleted!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='<< TRANSACTIONS MENU', callback_data='show_transactions')]
            ]
        )
    )
    await callback.answer()

    