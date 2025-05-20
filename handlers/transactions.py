
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from form import Form
from models import UserModel
from keyboards import main_menu
from repositories import UserRepository, TransactionRepository

user_repository = UserRepository()
transaction_repository = TransactionRepository()

router = Router()

@router.message(Command(commands=['transactions']))
async def cmd_get_transactions(message: types.Message, command: CommandObject, state: FSMContext):
    await state.set_state(Form.waiting_for_income)

    id = message.from_user.id
    username = message.from_user.username

    usr = await user_repository.find_one_by_username(username)
    if usr is None:
        usr = await user_repository.store(user=UserModel(username=username, user_id=id))

    transactions = await transaction_repository.find_all_by_user_id(usr.id)
    lines = ['Transactions:']
    for transaction in transactions:
        text = (
            f"{transaction.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"{transaction.type.value}: {transaction.amount:.2f} mdl"
        )
        lines.append(text)

    text = '\n\n'.join(lines)

    await message.answer(
        text,
        reply_markup=main_menu,
    )
    await state.clear()

