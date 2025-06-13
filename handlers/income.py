
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from form import Form
from keyboards.keyboards import get_back_to_menu_inline
from repositories import UserRepository, TransactionRepository, CategoryRepository
from utils import get_or_create_user
from models import TransactionModel, UserModel
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from enums import TransactionType

user_repository = UserRepository()
transaction_repository = TransactionRepository()
category_repository = CategoryRepository()
add_income_messages = ['add income', 'income']

router = Router()

@router.message(Command(commands=['add_income', 'income']))
@router.message(lambda message: message.text.lower() in add_income_messages)
async def cmd_add_income(message: types.Message, state: FSMContext):
    id = message.from_user.id
    username = message.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)
    
    await message.answer(
        "Select income category",
        reply_markup=get_income_categories_inline()
    )

@router.callback_query(F.data.startswith("add_income_category:"))
async def handle_category_click(callback: types.CallbackQuery, state: FSMContext):
    category_name = callback.data.split("add_income_category:")[1]
    await state.update_data(category=category_name)
    await callback.message.answer(f"Input income:")
    await state.set_state(Form.waiting_for_income)
    await callback.answer()

@router.callback_query(F.data == 'add_income' or F.data == 'add_income')
async def cmd_add_income_callback(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    id = message.from_user.id
    username = message.from_user.username
    await get_or_create_user(username=username, user_id=id)

    await callback.message.edit_text(
        "Select income category",
        reply_markup=get_income_categories_inline()
    )


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
    category_label = category_repository.get_category_label('income', category_name)
    if not category_name:
        await message.answer(
            "Error! category not set", 
            reply_markup=get_back_to_menu_inline()
        )
    if user:
        transaction = TransactionModel(
            type=TransactionType.INCOME, 
            user_id=user.id,
            amount=int(message.text),
            category=category_name
        )
    await transaction_repository.store(transaction=transaction)
    await state.clear()
    await message.answer(
        f"Income saved in category {category_label}", 
        reply_markup=get_back_to_menu_inline()
    )



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
