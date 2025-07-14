from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

from models import CurrencyModel
from repositories import CurrencyRepository, TransactionRepository


router = Router()
currencies_repository = CurrencyRepository()
transactions_repository = TransactionRepository()

show_currencies_messages = ['currencies']

@router.message(Command(commands=show_currencies_messages))
@router.message(lambda message: message.text.lower() in show_currencies_messages)
async def show_all_currencies(message: Message):

    await message.answer(
        "Currencies:",
        reply_markup = await create_currencies_buttons_list()
    )

@router.callback_query(F.data.in_(['currencies']))
async def show_all_currencies_callback(callback: CallbackQuery):

    await callback.message.edit_text(
        "Currencies:",
        reply_markup = await create_currencies_buttons_list()
    )
    await callback.answer()


async def create_currencies_buttons_list() -> InlineKeyboardMarkup:
    currencies = await currencies_repository.find_all()
    buttons = []
    for currency in currencies:
        buttons.append([InlineKeyboardButton(text=f"({currency.code}) {currency.label}", callback_data="empty")])
    buttons.append([
        InlineKeyboardButton(text='<< MENU', callback_data='menu'),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard