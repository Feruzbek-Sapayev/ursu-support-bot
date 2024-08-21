from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

send_phone = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text="☎️Telefon raqamini yuborish", request_contact=True)]
])

main_markup = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='✍🏻 Ariza yuborish')],
])

send_app = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='📩Yuborish')],
])

end_app = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='🏁Yakunlash'), KeyboardButton(text='💬Chatni boshlash')],
])

user_chat_btn = ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[
    [KeyboardButton(text='↩️Javob yozish')],
])