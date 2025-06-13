from aiogram import Router
from aiogram.types import Message
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command(commands=['manual', 'man', 'instructions', 'commands', 'help']))
@router.message(lambda message: message.text.lower() in ['manual', 'man', 'instructions', 'commands', 'help'])
async def cmd_get_manual(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Select option:",
        # reply_markup=get_manual_inline()
    )