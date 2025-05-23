from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

# inline keyboards


def get_main_menu_inline(id)->InlineKeyboardMarkup:
    main_menu_inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Add income', callback_data='add_income')],
            [InlineKeyboardButton(text='Add expense', callback_data='add_expense')],
            [InlineKeyboardButton(text='Show statistic', callback_data='show_stats')],
        ]
    )
    return main_menu_inline


def get_back_to_stats_inline()->InlineKeyboardMarkup:
    back_to_stats_inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='<< BACK', callback_data='show_stats')],
        ]
    )
    return back_to_stats_inline

def get_back_to_category_types_inline()->InlineKeyboardMarkup:
    back_to_stats_inline = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='<< BACK', callback_data='categories')],
        ]
    )
    return back_to_stats_inline

def get_statistic_options_inline()->InlineKeyboardMarkup:
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
    return statistic_options_inline


def get_category_types_inline()->InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Income', callback_data='show_categories_income'),
                InlineKeyboardButton(text='Expense', callback_data='show_categories_expense')
            ]
        ]
    )
    return markup



# simple keyboards
def get_main_menu():
    main_menu = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Add income'), KeyboardButton(text='Add expense')],
            [KeyboardButton(text='Show statistic')],
        ],
        resize_keyboard=True
    )
    return main_menu




