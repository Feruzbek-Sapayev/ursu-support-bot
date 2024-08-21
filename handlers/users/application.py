import asyncio
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from loader import db, bot
from data.config import ADMINS, GROUP_ID
from utils.extra_datas import make_title
from states.test import UserState
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from keyboards.reply import buttons as reply_buttons
from keyboards.inline import buttons as inline_buttons
import json
from datetime import datetime

router = Router()


@router.message(UserState.application)
async def get_app(message: types.Message, state: FSMContext):
    if message.text and message.text == "📩Yuborish":
        messages = json.dumps((await state.get_data()).get('messages'))
        user = await db.select_user(telegram_id=message.from_user.id)
        now = datetime.now()
        application = await db.add_application(applicant=user['id'], files=messages, status='Yangi', admin=None, created=now, group_message='')
        text = f'<b>📥 Yangi ariza #{application["id"]}</b>\n\n<b>👤Arizachi:</b> <a href="tg://user?id={message.from_user.id}">{user["full_name"]}</a>\n<b>⏰Vaqt:</b> {now.strftime("%d.%m.%Y %H:%M:%S")}\n<b>🎗Status:</b> Yangi'
        markup = inline_buttons.accept_or_decline_markup(application['id'])
        gr_msg = await bot.send_message(chat_id=GROUP_ID, text=text, reply_markup=markup)
        db_gr_msg = json.dumps({'message_id': gr_msg.message_id, 'text': text})
        await db.update_application_group_message(db_gr_msg, application['id'])
        await message.answer("Arizangiz tez orada ko'rib chiqiladi!", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        if message.media_group_id:
            await message.reply('Mediafayllarni alohida yuboring!')
        else:
            data = (await state.get_data()).get('messages')
            if message.content_type == 'text':
                data.append({'type': 'text', 'text': message.html_text})
            elif message.content_type == 'photo':  
                data.append({'type': 'photo', 'caption': message.html_text, 'photo': message.photo[-1].file_id})
            elif message.content_type == 'video':
                data.append({'type': 'video', 'caption': message.html_text, 'video': message.video.file_id})
            elif message.content_type == 'document':
                data.append({'type': 'document', 'caption': message.html_text, 'document': message.document.file_id})
            elif message.content_type == 'voice':
                data.append({'type': 'audio', 'caption': message.html_text, 'voice': message.voice.file_id,})
            else:
                await message.answer(text="Arizangizni <i>text</i>, <i>rasm</i>, <i>video</i>, <i>dokument</i> yoki <i>audio</i> ko'rinishda yuboring va <b>📩Yuborish</b> tugmasini bosing:", reply_markup=reply_buttons.send_app)              
            await state.update_data({'messages': data})
