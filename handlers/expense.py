from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from enums import TransactionType
from form import Form
from keyboards.keyboards import get_back_to_menu_inline
from models.Transaction import TransactionModel
from models.User import UserModel
from utils import get_or_create_user
from repositories import UserRepository, TransactionRepository, CategoryRepository
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

user_repository = UserRepository()
transaction_repository = TransactionRepository()
category_repository = CategoryRepository()
add_expense_messages = ['add expense', 'expense']

router = Router()

@router.message(Command(commands=['add_expense', 'expense']))
@router.message(lambda message: message.text.lower() in add_expense_messages)
async def cmd_add_expense(message: types.Message, state: FSMContext):
    id = message.from_user.id
    username = message.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)

    await message.answer(
        "Select expense category",
        reply_markup=get_expense_categories_inline()
    )

@router.callback_query(F.data.startswith("add_expense_category:"))
async def handle_category_click(callback: types.CallbackQuery, state: FSMContext):
    category_name = callback.data.split("add_expense_category:")[1]
    await state.update_data(category=category_name)
    await callback.message.answer(f"Input expense:")
    await state.set_state(Form.waiting_for_expense)
    await callback.answer()

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
    category_label = category_repository.get_category_label('expense', category_name)
    if not category_name:
        await message.answer(
            "Error! category not set", 
            reply_markup=get_back_to_menu_inline()
        )

    if user:
        transaction = TransactionModel(
            type=TransactionType.EXPENSE, 
            user_id=user.id,
            amount=int(message.text),
            category=category_name
        )
        
    await transaction_repository.store(transaction=transaction)
    await state.clear()
    await message.answer(
        f"Expense saved in category {category_label}", 
        reply_markup=get_back_to_menu_inline()
    )

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
    

