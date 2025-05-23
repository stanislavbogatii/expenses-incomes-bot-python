from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton


main_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Add income', callback_data='add_income')],
        [InlineKeyboardButton(text='Add expense', callback_data='add_expense')],
        [InlineKeyboardButton(text='Show statistic', callback_data='show_stats')],
    ]
)

back_to_stats_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='<< BACK', callback_data='show_stats')],
    ]
)

statistic_options_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Day', callback_data='stats_period_day'),
            InlineKeyboardButton(text='Week', callback_data='stats_period_week'),
            InlineKeyboardButton(text='Month', callback_data='stats_period_month')
        ],
        [
            InlineKeyboardButton(text='3 Month', callback_data='stats_period_three_months'),
            InlineKeyboardButton(text='6 Month', callback_data='stats_period_six_months'),
            InlineKeyboardButton(text='Year', callback_data='stats_period_year')
        ],
        [InlineKeyboardButton(text='All time', callback_data='stats_period_all')],
    ]
)

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Add income'), KeyboardButton(text='Add expense')],
        [KeyboardButton(text='Show statistic')],
    ],
    resize_keyboard=True
)