from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from enums import TransactionType
from form import Form
from keyboards import get_main_menu
from models.Transaction import TransactionModel
from models.User import UserModel
from utils import get_or_create_user
from repositories import UserRepository, TransactionRepository

user_repository = UserRepository()
transaction_repository = TransactionRepository()

router = Router()

@router.message(Command(commands=['add_expense', 'expense']))
async def cmd_add_expense(message: types.Message, command: CommandObject, state: FSMContext):
    id = message.from_user.id
    username = message.from_user.username
    user: UserModel = await get_or_create_user(username=username, user_id=id)
    amount = command.args
    if amount and amount.isdigit():
        if user:
            transaction = TransactionModel(
                type=TransactionType.EXPENSE, 
                user_id=user.id,
                amount=int(amount)
            )
            await transaction_repository.store(transaction=transaction)
            await state.clear()
            await message.answer("Expense saved!", reply_markup=get_main_menu())
            return
        
    await state.set_state(Form.waiting_for_expense)
    await message.answer(
        "Input expense"
    )

@router.message(lambda message: message.text == "Add expense")
async def cmd_add_expense(message: types.Message, state: FSMContext):
    id = message.from_user.id
    username = message.from_user.username
    await get_or_create_user(username=username, user_id=id)
        
    await state.set_state(Form.waiting_for_expense)
    await message.answer(
        "Input expense"
    )

@router.callback_query(F.data == 'add_expense' or F.data == 'expense')
async def cmd_add_expense(callback: types.CallbackQuery, state: FSMContext):
    message = callback.message
    id = message.from_user.id
    username = message.from_user.username
    await get_or_create_user(username=username, user_id=id)
        
    await state.set_state(Form.waiting_for_expense)
    await callback.message.answer(
        "Input expense"
    )
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
    if user:
        transaction = TransactionModel(
            type=TransactionType.EXPENSE, 
            user_id=user.id,
            amount=int(message.text)
        )
    await transaction_repository.store(transaction=transaction)
    await state.clear()
    await message.answer("Expense saved!", reply_markup=get_main_menu())