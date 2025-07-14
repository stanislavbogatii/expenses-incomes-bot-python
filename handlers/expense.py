from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from enums import TransactionType
from form import Form
from keyboards.keyboards import get_back_to_menu_inline, get_catch_error_inline
from models.Transaction import TransactionModel
from models.User import UserModel
from utils import get_or_create_user
from repositories import UserRepository, CurrencyRepository, TransactionRepository, CategoryRepository
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

user_repository = UserRepository()
transaction_repository = TransactionRepository()
category_repository = CategoryRepository()
currency_repository = CurrencyRepository()
add_expense_messages = ['add expense', 'expense', 'exp']

router = Router()

# handlers
@router.message(Command(commands=['add_expense', 'expense', 'exp']))
@router.message(lambda message: message.text.lower() in add_expense_messages)
async def cmd_add_expense(message: types.Message, state: FSMContext):
    id = message.from_user.id
    username = message.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)

    await message.answer(
        "Select expense category",
        reply_markup=get_expense_categories_inline()
    )

@router.callback_query(F.data == 'add_expense' or F.data == 'expense')
async def cmd_add_expense(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    id = message.from_user.id
    username = message.from_user.username
    await get_or_create_user(username=username, user_id=id)

    await callback.message.edit_text(
        "Select expense category",
        reply_markup=get_expense_categories_inline()
    )

@router.callback_query(F.data.startswith("add_expense_category:"))
async def handle_category_click(callback: types.CallbackQuery, state: FSMContext):
    category_name = callback.data.split("add_expense_category:")[1]
    await state.update_data(category=category_name)

    await callback.message.edit_text(
        "Select expense currency:",
        reply_markup=await get_currencies_inline()
    )
    await state.set_state(Form.waiting_for_expense_currency)
    await callback.answer()


@router.callback_query(F.data.startswith("expense_currency:"), Form.waiting_for_expense_currency)
async def cmd_waiting_for_expense_currency(callback: types.CallbackQuery, state: FSMContext):
    currency = callback.data.split("expense_currency:")[1]
    await state.update_data(currency=currency)

    await callback.message.answer(f"Input expense:")
    await state.set_state(Form.waiting_for_expense)
    await callback.answer()

@router.message(Form.waiting_for_expense)
async def cmd_waiting_for_expense(message: types.Message, state: FSMContext):
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
    category_label = category_repository.get_category_label('expense', category_name)
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
            type=TransactionType.EXPENSE, 
            user_id=user.id,
            currency=currency.code,
            amount=int(message.text),
            category=category_name
        )
        
    await transaction_repository.store(transaction=transaction)
    await state.clear()
    await message.answer(
        f"Expense saved in category {category_label}", 
        reply_markup=get_back_to_menu_inline()
    )





# functions
def get_expense_categories_inline():
    categories = category_repository.find_all_by_type('expense')
    buttons = [
        [
            InlineKeyboardButton(text=categories[i]['label'], callback_data=f"add_expense_category:{categories[i]['value']}"),
            InlineKeyboardButton(text=categories[i + 1]['label'], callback_data=f"add_expense_category:{categories[i + 1]['value']}")
        ]
        for i in range(0, len(categories) - 1, 2)
    ]
    if len(categories) % 2 != 0:
        buttons.append([
            InlineKeyboardButton(text=categories[-1]['label'], callback_data=f"add_expense_category:{categories[-1]['value']}")
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
        buttons.append([InlineKeyboardButton(text=f"({currency.code}) {currency.label}", callback_data=f"expense_currency:{currency.code}")])
    buttons.append([
        InlineKeyboardButton(text='<< MENU', callback_data='menu'),
    ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
    

