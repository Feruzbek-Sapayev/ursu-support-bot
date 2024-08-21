from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


inline_keyboard = [[
    InlineKeyboardButton(text="✅ Yes", callback_data='yes'),
    InlineKeyboardButton(text="❌ No", callback_data='no')
]]
are_you_sure_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

def accept_or_decline_markup(app_id):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='✅Qabul qilish', callback_data=f'accept_{app_id}'), InlineKeyboardButton(text='❎Bekor qilish', callback_data=f"decline_{app_id}")]
    ])
    return markup


def rating_btns(admin):
    rating_markup = InlineKeyboardMarkup(inline_keyboard=[])
    btn = []
    for i in range(1, 6):
        btn.append(InlineKeyboardButton(text='⭐', callback_data=f"rating_{i}_{admin}"))
    rating_markup.inline_keyboard.append(btn)
    return rating_markup

