from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from form import Form
from keyboards import main_menu_inline

router = Router()

@router.message(Command(commands=['start']))
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "Hi, select options:",
        reply_markup=main_menu_inline,
    )
    await state.clear()
