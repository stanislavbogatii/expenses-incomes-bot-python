from aiogram import Dispatcher
from .start import router as start_router
from .income import router as income_router
from .expense import router as expense_router
from .transactions import router as transactions_router
from .statistic import router as statistic_router
from .default import router as default_router
from .categories import router as categories_router
from .transaction import router as transaction_router
from .users import router as users_router
from .support import router as support_router

def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(income_router)
    dp.include_router(expense_router)
    dp.include_router(transactions_router)
    dp.include_router(statistic_router)
    dp.include_router(categories_router)
    dp.include_router(transaction_router)
    dp.include_router(users_router)
    dp.include_router(support_router)
    dp.include_router(default_router)