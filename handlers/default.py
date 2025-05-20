from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(F.text)
async def catch_all_texts(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Not a command")