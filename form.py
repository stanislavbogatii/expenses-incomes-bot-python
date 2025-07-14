from aiogram.fsm.state import State, StatesGroup

class Form (StatesGroup):
    waiting_for_income = State()
    waiting_for_expense = State()
    waiting_for_expense_currency = State()
    waiting_for_income_currency = State()
    waiting_for_category_name = State()
    waiting_for_custom_transactions_period = State()
    waiting_for_custom_stats_period = State()
    waiting_for_write_bug_report = State()