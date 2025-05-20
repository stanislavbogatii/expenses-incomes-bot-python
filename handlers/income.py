
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from form import Form
from keyboards import main_menu
from repositories import UserRepository, TransactionRepository
from utils import get_or_create_user
from models import TransactionModel, UserModel
from enums import TransactionType

user_repository = UserRepository()
transaction_repository = TransactionRepository()

router = Router()

@router.message(Command(commands=['add_income']))
@router.message(lambda message: message.text == "Add income")
async def cmd_add_income(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_income)

    await message.answer(
        "Input income",
        reply_markup=main_menu,
    )

@router.callback_query(F.data == 'add_income')
async def cmd_add_income_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_income)

    await callback.message.answer(
        "Input income",
        reply_markup=main_menu,
    )
    await callback.answer()

@router.message(Form.waiting_for_income)
async def cmd_waiting_for_income(message: types.message, state: FSMContext):
    if not message.text.isdigit():
        await state.clear()
        await message.answer("*Input digit*")
        return
    
    id = message.from_user.id
    username = message.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)
    if user:
        transaction = TransactionModel(
            type=TransactionType.INCOME, 
            user_id=user.id,
            amount=int(message.text)
        )
    await transaction_repository.store(transaction=transaction)
    await state.clear()
    await message.answer("Income saved!")
