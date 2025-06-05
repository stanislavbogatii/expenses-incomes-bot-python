
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command, CommandObject
from form import Form
from enums import CategoryType
from models import UserModel
from keyboards import get_category_types_inline, get_back_to_category_types_inline, get_category_types_create_inline
from repositories import UserRepository, TransactionRepository, CategoryRepository
from utils import get_or_create_user

user_repository = UserRepository()
transaction_repository = TransactionRepository()
category_repository = CategoryRepository()

router = Router()

# @router.callback_query(F.data.startswith('show_categories_'))
# async def show_categories_by_type(callback: CallbackQuery):
#     message = callback.message
#     category_type: CategoryType = callback.data.replace('show_categories_', '')
#     id = callback.from_user.id
#     username = callback.from_user.username
#     user: UserModel = await get_or_create_user(username=username, user_id=id)

#     categories = await category_repository.find_all_by_type(category_type)

#     await message.edit_text(
#         f"{category_type} categories",
#         reply_markup=get_back_to_category_types_inline()
#     )
#     await callback.answer()


# @router.callback_query(F.data == "categories")
# async def show_category_types(callback: CallbackQuery, state: FSMContext):
#     message = callback.message
#     id = callback.from_user.id
#     username = callback.from_user.username

#     user: UserModel = await get_or_create_user(username=username, user_id=id)

#     await message.edit_text(
#         'Select type',
#         reply_markup=get_category_types_inline(),
#     )
#     await state.clear()
#     await callback.answer()

# @router.message(Command(commands=['categories']))
# async def show_category_types(message: Message, command: CommandObject, state: FSMContext):
#     id = message.from_user.id
#     username = message.from_user.username

#     user: UserModel = await get_or_create_user(username=username, user_id=id)

#     await message.answer(
#         'Select type',
#         reply_markup=get_category_types_inline(),
#     )
#     await state.clear()



# Create categories
# @router.message(Command(commands=['create_category']))
# async def create_category(message: Message, command: CommandObject, state: FSMContext):
#     id = message.from_user.id
#     username = message.from_user.username
#     user: UserModel = await get_or_create_user(username=username, user_id=id)

#     await message.answer(
#         'Select type for new category:',
#         reply_markup=get_category_types_create_inline()
#     )
#     await state.clear()


# @router.callback_query(F.data.startswith('create_category_'))
# async def create_category_by_type(callback: CallbackQuery):
#     message = callback.message
#     category_type: CategoryType = callback.data.replace('create_category_', '')
#     id = callback.from_user.id
#     username = callback.from_user.username
#     user: UserModel = await get_or_create_user(username=username, user_id=id)

    

#     await message.edit_text(
#         f"Category name: ",
#         reply_markup=get_back_to_category_types_inline()
#     )
#     await callback.answer()