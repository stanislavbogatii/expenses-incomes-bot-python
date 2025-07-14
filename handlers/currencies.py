from aiogram import Router, F
from aiogram.filters.command import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from services import CurrencyExchangeService

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


@router.callback_query(F.data.startswith('show_currencies:'))
async def cmd_show_currencies_for_source(callback: CallbackQuery):
    currency_code = callback.data.split("show_currencies:")[1]
    quotes = await CurrencyExchangeService.get_currencies_by_source(currency_code)
    await callback.message.edit_text(
        "Actual courses",
        reply_markup=create_currenies_by_source_list(quotes)
    )
    await callback.answer()
    


# functions
async def create_currencies_buttons_list() -> InlineKeyboardMarkup:
    currencies = await currencies_repository.find_all()
    buttons = []
    for currency in currencies:
        buttons.append([InlineKeyboardButton(text=f"({currency.code}) {currency.label} {currency.symbol}", callback_data=f"show_currencies:{currency.code}")])
    buttons.append([
        InlineKeyboardButton(text='<< MENU', callback_data='menu'),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def create_currenies_by_source_list(quotes: dict) -> InlineKeyboardMarkup:
    buttons = []
    for pair, rate in quotes.items():
        buttons.append([InlineKeyboardButton(text=f"{pair} : {rate}", callback_data=f"empty")])
    buttons.append([
        InlineKeyboardButton(text='<< BACK', callback_data='currencies'),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard