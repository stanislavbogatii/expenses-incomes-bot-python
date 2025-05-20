from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton


main_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Добавить доход', callback_data='add_income')],
        [InlineKeyboardButton(text='Добавить расход', callback_data='add_expense')],
        [InlineKeyboardButton(text='Показать статистику', callback_data='show_stats')],
    ]
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Add income', callback_data='add_income'), KeyboardButton(text='Добавить доход3', callback_data='add_income3')],
        [KeyboardButton(text='Add expence', callback_data='add_expense'), KeyboardButton(text='Показать статистику', callback_data='show_stats')],
    ],
    resize_keyboard=True
)