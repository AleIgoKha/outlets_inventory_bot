from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏪 Торговые точки', callback_data='outlets:choose_outlet')]
    # [InlineKeyboardButton(text='🧀 Продукты', callback_data='products:list')],
])