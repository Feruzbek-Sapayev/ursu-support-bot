from aiogram import Router, types
from aiogram.filters import CommandStart
from loader import db, bot
from data.config import ADMINS
from utils.extra_datas import make_title
from states.test import SignUp, UserState
from aiogram.fsm.context import FSMContext
from keyboards.reply.buttons import send_phone, main_markup

router = Router()


@router.message(SignUp.full_name)
async def get_full_name(message: types.Message, state: FSMContext):
    if message.text:
        full_name = message.text
        if len(message.text) > 7:
            await state.set_data({'full_name': full_name})
            await message.answer('Telefon raqamingizni <i>+998.........</i> formatda kiriting yoki quyidagi tugmani bosing:', reply_markup=send_phone)
            await state.set_state(SignUp.phone_number)
        else:
            await message.answer("Ism va familiya uzunligi juda qisqa. Iltimos, ma`lumotlarni to'liq kiriting:")
    else:
        await message.answer("Iltimos, ism va familiyangizni kiriting:")

@router.message(SignUp.phone_number)
async def get_phone_number(message: types.Message, state: FSMContext):
    if message.text:
        phone_number = message.text
    elif message.contact:
        phone_number = message.contact.phone_number
    else:
        await message.answer('Telefon raqamingizni <i>+998.........</i> formatda kiriting yoki quyidagi tugmani bosing:', reply_markup=send_phone)

    if len(phone_number) == 13 and phone_number[1:].isdigit() and phone_number[0] == '+':
        telegram_id = message.from_user.id
        full_name = (await state.get_data()).get('full_name')
        username = message.from_user.username
        await db.add_user(full_name, username, telegram_id, phone_number)
        await message.answer("Ro'yxatdan o'tish yakunlandi. Botdan foydalanishingiz mumkin!", reply_markup=main_markup)
        await state.set_state(UserState.main)
    else:
        await message.answer('Telefon raqamingizni <i>+998.........</i> formatda kiriting yoki quyidagi tugmani bosing:', reply_markup=send_phone)
