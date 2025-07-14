from aiogram import Router, F
from aiogram.types import CallbackQuery
from repositories import TransactionRepository
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


router = Router()
transaction_repository = TransactionRepository()

@router.callback_query(F.data.startswith('open_transaction_'))
async def open_transaction(callback: CallbackQuery):
    id = callback.data.replace('open_transaction_', '')
    transaction = await transaction_repository.find_one_by_id(id)
    await callback.message.edit_text(
        f"{transaction.type.value} {transaction.created_at.strftime('%d.%m.%Y')} {transaction.amount:.2f} {transaction.currency} ({transaction.category})",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='DELETE', callback_data='confirm_delete_transaction_'+id)],
                [InlineKeyboardButton(text='<< BACK', callback_data='show_transactions')]
            ]
        )
    )
    await callback.answer()

@router.callback_query(F.data.startswith('confirm_delete_transaction_'))
async def confirm_delete_transaction(callback: CallbackQuery):
    id = callback.data.replace('confirm_delete_transaction_', '')
    transaction = await transaction_repository.find_one_by_id(id)
    await callback.message.edit_text(
        f"Are you sure you want to delete {transaction.type.value} {transaction.created_at.strftime('%d.%m.%Y')} {transaction.amount:.2f} {transaction.currency} ({transaction.category})?",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='YES', callback_data='delete_transaction_'+id)],
                [InlineKeyboardButton(text='NO', callback_data='open_transaction_'+id)]
            ]
        )
    )
    await callback.answer()

@router.callback_query(F.data.startswith('delete_transaction_'))
async def confirm_delete_transaction(callback: CallbackQuery):
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

    