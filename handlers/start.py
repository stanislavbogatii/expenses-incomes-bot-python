from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from form import Form
from keyboards.keyboards import get_main_menu_inline
from utils import get_or_create_user

router = Router()

@router.message(Command(commands=['start', 'menu', 'home']))
@router.message(lambda message: message.text.lower() in ['start', 'menu', 'home', 'cd ~', 'cd /'])
async def cmd_start(message: types.Message, state: FSMContext):
    id = message.from_user.id
    username = message.from_user.username
    await get_or_create_user(username, id)
    print(username, id)
    await message.answer(
        "Hi, select options:",
        reply_markup=get_main_menu_inline(),
    )
    await state.clear()

@router.callback_query(F.data.in_(['start', 'menu']))
async def cmd_start_callback(callback: types.CallbackQuery, state: FSMContext):
    id = callback.from_user.id
    username = callback.from_user.username
    await get_or_create_user(username, id)
    print(username, id)
    await callback.message.edit_text(
        "Hi, select options:",
        reply_markup=get_main_menu_inline(),
    )
    await state.clear()
    await callback.answer()