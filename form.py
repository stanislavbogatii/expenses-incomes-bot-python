from aiogram.fsm.state import State, StatesGroup

class Form (StatesGroup):
    waiting_for_income = State()
    waiting_for_expense = State()
    waiting_for_category_name = State()