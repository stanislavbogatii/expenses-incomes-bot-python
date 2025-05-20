from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from form import Form
from keyboards import main_menu_inline

router = Router()

@router.message(Command(commands=['add_expense']))
@router.message(lambda message: message.text == "Add expense")
async def cmd_add_expense(message: types.Message, state: FSMContext):
    await state.set_state(Form.waiting_for_expense)
    await message.answer(
        "Input expense"
    )

@router.callback_query(F.data == 'add_expense')
async def cmd_add_expense(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.waiting_for_expense)
    await callback.message.answer(
        "Input expense"
    )
    await callback.answer()


@router.message(Form.waiting_for_expense)
async def cmd_waiting_for_expense(message: types.message, state: FSMContext):
    print(message.text)
    await state.clear()