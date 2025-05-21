from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton


main_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Add income', callback_data='add_income')],
        [InlineKeyboardButton(text='Add expense', callback_data='add_expense')],
        [InlineKeyboardButton(text='Show statistic', callback_data='show_stats')],
    ]
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Add income'), KeyboardButton(text='Add expense')],
        [KeyboardButton(text='Show statistic')],
    ],
    resize_keyboard=True
)