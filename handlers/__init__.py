from aiogram import Dispatcher
from .start import router as start_router
from .income import router as income_router
from .expense import router as expense_router

def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(income_router)
    dp.include_router(expense_router)