
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from form import Form
from keyboards.keyboards import get_back_to_menu_inline, get_catch_error_inline
from repositories import UserRepository, TransactionRepository, CategoryRepository, CurrencyRepository
from utils import get_or_create_user
from models import TransactionModel, UserModel
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from enums import TransactionType

user_repository = UserRepository()
transaction_repository = TransactionRepository()
category_repository = CategoryRepository()
currency_repository = CurrencyRepository()

add_income_messages = ['add income', 'income', 'inc']

router = Router()

# handlers
@router.message(Command(commands=['add_income', 'income', 'inc']))
@router.message(lambda message: message.text.lower() in add_income_messages)
async def cmd_add_income(message: types.Message, state: FSMContext):
    id = message.from_user.id
    username = message.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)
    
    await message.answer(
        "Select income category",
        reply_markup=get_income_categories_inline()
    )

@router.callback_query(F.data == 'add_income' or F.data == 'add_income')
async def cmd_add_income_callback(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    id = message.from_user.id
    username = message.from_user.username
    await get_or_create_user(username=username, user_id=id)

    await callback.message.edit_text(
        "Select income category",
        reply_markup=get_income_categories_inline(),        
    )

@router.callback_query(F.data.startswith("add_income_category:"))
async def handle_category_click(callback: types.CallbackQuery, state: FSMContext):
    category_name = callback.data.split("add_income_category:")[1]
    await state.update_data(category=category_name)

    await callback.message.edit_text(
        "Select income currency:",
        reply_markup=await get_currencies_inline()
    )
    await state.set_state(Form.waiting_for_income_currency)
    await callback.answer()

@router.callback_query(F.data.startswith("income_currency:"), Form.waiting_for_income_currency)
async def cmd_waiting_for_expense_currency(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("income_currency:")[1]
    await state.update_data(currency=currency)

    await callback.message.answer(f"Input income:")
    await state.set_state(Form.waiting_for_income)
    await callback.answer()


@router.message(Form.waiting_for_income)
async def cmd_waiting_for_income(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await state.clear()
        await message.answer("*Input digit*")
        return
    
    id = message.from_user.id
    username = message.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)
    data = await state.get_data()

    category_name = data.get("category")
    currency_code = data.get("currency")
    category_label = category_repository.get_category_label('income', category_name)
    currency = await currency_repository.find_one_by_code(currency_code)
    
    if not currency: 
        await message.answer(
            "Currency not found. Please try again or contact support for help.",
            reply_markup=get_catch_error_inline()
        )

    if not category_name:
        await message.answer(
            "Error! category not set", 
            reply_markup=get_catch_error_inline()
        )
    if user:
        transaction = TransactionModel(
            type=TransactionType.INCOME, 
            user_id=user.id,
            amount=int(message.text),
            currency=currency.code,
            category=category_name
        )
    await transaction_repository.store(transaction=transaction)
    await state.clear()
    await message.answer(
        f"Income saved in category {category_label}", 
        reply_markup=get_back_to_menu_inline()
    )


# functions
def get_income_categories_inline():
    categories = category_repository.find_all_by_type('income')
    buttons = [
        [
            InlineKeyboardButton(text=categories[i]['label'], callback_data=f"add_income_category:{categories[i]['value']}"),
            InlineKeyboardButton(text=categories[i + 1]['label'], callback_data=f"add_income_category:{categories[i + 1]['value']}")
        ]
        for i in range(0, len(categories) - 1, 2)
    ]
    if len(categories) % 2 != 0:
        buttons.append([
            InlineKeyboardButton(text=categories[-1]['label'], callback_data=f"add_income_category:{categories[-1]['value']}")
        ])
    buttons.append([
        InlineKeyboardButton(text='<< MENU', callback_data='menu')
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

async def get_currencies_inline():
    currencies = await currency_repository.find_all()
    buttons = []
    for currency in currencies:
        buttons.append([InlineKeyboardButton(text=f"({currency.code}) {currency.label}", callback_data=f"income_currency:{currency.code}")])
    buttons.append([
        InlineKeyboardButton(text='<< MENU', callback_data='menu'),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
