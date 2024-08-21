from aiogram import Router, types
from aiogram.filters import CommandStart
from loader import db, bot
from data.config import ADMINS
from utils.extra_datas import make_title
from states.test import SignUp, UserState, AdminsState
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from keyboards.reply.buttons import main_markup, end_app
import json

router = Router()


@router.message(CommandStart())
async def do_start(message: types.Message, state: FSMContext):
    telegram_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username
    user = await db.select_user(telegram_id=telegram_id)
    admin = await db.select_admin(telegram_id=telegram_id)
    if admin:
        await message.answer(f'Salom admin {full_name}.')
        application = await db.select_application(admin=admin['id'], status='Jarayonda')
        if application:
            applicant = await db.select_user(id=application['applicant'])
            text = f'<b>Siz #{application["id"]} raqamli arizani yakunlamadingiz!</b>\n\n<b>👤Arizachi:</b> <a href="tg://user?id={applicant["telegram_id"]}">{applicant["full_name"]}</a>'
            await message.answer(text, reply_markup=end_app)
            messages = json.loads(application['files'])
            for msg in messages:
                if msg.get('type') == 'text':
                    await bot.send_message(chat_id=admin['telegram_id'], text=msg.get('text'))
                if msg.get('type') == 'photo':
                    await bot.send_photo(chat_id=admin['telegram_id'], photo=msg.get('photo'), caption=msg.get('caption'))
                if msg.get('type') == 'video':
                    await bot.send_video(chat_id=admin['telegram_id'], video=msg.get('video'), caption=msg.get('caption'))
                if msg.get('type') == 'document':
                    await bot.send_document(chat_id=admin['telegram_id'], document=msg.get('document'), caption=msg.get('caption'))
                if msg.get('type') == 'audio':
                    await bot.send_audio(chat_id=admin['telegram_id'], audio=msg.get('audio'), caption=msg.get('caption'))  
    else:
        if user:
            user_application_1 = await db.select_application(applicant=user['id'], status='Jarayonda')
            user_application_2 = await db.select_application(applicant=user['id'], status='Yangi')
            if user_application_1:
                await message.answer(f"Sizning <b>{user_application_1['created'].strftime('%d.%m.%Y %H:%M')}</b> da bergan arizangiz ko'rib chiqilmoqda...", reply_markup=ReplyKeyboardRemove())
            elif user_application_2:
                await message.answer(f"Sizning <b>{user_application_2['created'].strftime('%d.%m.%Y %H:%M')}</b> da bergan arizangiz navbatda.", reply_markup=ReplyKeyboardRemove())
            else:
                await state.set_state(UserState.main)
                await message.answer_photo(photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdMvkY0y2YQOdodWlwFhIcUYSlMNb3vc4vVg&s', caption=f"👋Assalomu alaykum {full_name}. <b>Urganch Davlat Universitetining</b> rasmiy botiga xush kelibsiz!", parse_mode='html', reply_markup=main_markup)

        else:
            await message.answer_photo(photo='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSdMvkY0y2YQOdodWlwFhIcUYSlMNb3vc4vVg&s', caption=f"👋Assalomu alaykum {full_name}. <b>Urganch Davlat Universitetining</b> rasmiy botiga xush kelibsiz!\n❗️Botdan foydalanish uchun avval ro'yxatdan o'ting.", parse_mode='html', reply_markup=ReplyKeyboardRemove())
            await message.answer('Ism va familiyangizni kiriting:')
            await state.set_state(SignUp.full_name)
            
