from aiogram import Router, types, F
from aiogram.filters import CommandStart
from loader import db, bot
from data.config import ADMINS, GROUP_ID
from utils.extra_datas import make_title
from states.test import UserState, AdminsState
from aiogram.fsm.context import FSMContext
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove
from keyboards.reply import buttons as reply_buttons
from keyboards.inline import buttons as inline_buttons
import json

router = Router()


@router.message(UserState.main)
async def main_handler(message: types.Message, state: FSMContext):
    if message.text:
        if message.text == "✍🏻 Ariza yuborish":
            user = await db.select_user(telegram_id=message.from_user.id)
            user_application = await db.select_application(applicant=user['id'], status='Jarayonda')
            if user_application:
                await message.answer('Sizda tugallanmagan ariza mavjud!')
            else:
                await message.answer(text="Arizangizni <i>text</i>, <i>rasm</i>, <i>video</i>, <i>dokument</i> yoki <i>audio</i> ko'rinishda yuboring va <b>📩Yuborish</b> tugmasini bosing:", reply_markup=reply_buttons.send_app)
                await state.set_state(UserState.application)
                await state.set_data({'messages': []})
    

@router.message(UserState.chat)
async def user_chat_handler(message: types.Message, state: FSMContext):
    if message.text == '↩️Javob yozish':
        user = await db.select_user(telegram_id=message.from_user.id)
        application = await db.select_application(applicant=user['id'], status='Jarayonda')
        if application:
            await message.answer('Marhamat, adminga yozishingiz mukin:')
        else:
            await message.answer('Siz hali ariza bermagansiz!')
    else:
        user = await db.select_user(telegram_id=message.from_user.id)
        application = await db.select_application(applicant=user['id'], status='Jarayonda')
        admin_id = application['admin']
        admin = await db.select_admin(id=admin_id)
        print(admin)
        await message.send_copy(chat_id=admin['telegram_id'])
        chat_msg = await db.select_chat_message(application=application['id'])
        if chat_msg is None:
            msgs = json.dumps([])
            chat_msg = await db.add_message_to_chat(application=application['id'], messages=msgs)
        if message.media_group_id:
            await message.reply('Mediafayllarni alohida yuboring!')
        else:
            messages = json.loads(chat_msg['messages'])
            if message.content_type == 'text':
                messages.append({'user': 'admin', 'type': 'text', 'text': message.html_text})
            elif message.content_type == 'photo':  
                messages.append({'user': 'admin', 'type': 'photo', 'caption': message.html_text, 'photo': message.photo[-1].file_id})
            elif message.content_type == 'video':
                messages.append({'user': 'admin', 'type': 'video', 'caption': message.html_text, 'video': message.video.file_id})
            elif message.content_type == 'document':
                messages.append({'user': 'admin', 'type': 'document', 'caption': message.html_text, 'document': message.document.file_id})
            elif message.content_type == 'voice':
                messages.append({'user': 'admin', 'type': 'audio', 'caption': message.html_text, 'voice': message.voice.file_id,})
            else:
                await message.answer(text="Xabarni <i>text</i>, <i>rasm</i>, <i>video</i>, <i>dokument</i> yoki <i>audio</i> ko'rinishda yuboring")              
            await db.update_chat_message(messages=json.dumps(messages), application=application['id'])


@router.message(AdminsState.chat)
async def admin_chat_handler(message: types.Message, state: FSMContext):
    applicant_telegram_id = int((await state.get_data()).get('applicant'))
    print(applicant_telegram_id)
    if message.text == "🏁Yakunlash":
        application_id = int((await state.get_data()).get('application'))
        await message.answer('Ariza yakunlandi!', reply_markup=ReplyKeyboardRemove())
        await state.clear()
        admin = await db.select_admin(telegram_id=message.from_user.id)
        application = await db.select_application(id=application_id)
        gr_msg = json.loads(application['group_message'])
        gr_message_id = gr_msg.get('message_id')
        gr_message_text = gr_msg.get('text')
        new_text = gr_message_text[:-21] + f'<b>👨🏻‍💻Qabul qildi:</b> <a href="tg://user?id={message.from_user.id}">{admin["full_name"]}</a>\n' + "<b>🎗Status:</b> Yakunlangan"
        await bot.edit_message_text(text=new_text, chat_id=GROUP_ID, message_id=gr_message_id)
        await db.update_admin_status(admin['applications'] + 1, admin['telegram_id'])
        await db.update_application_status('Yakunlangan', admin['id'], application_id)
        await bot.send_message(chat_id=applicant_telegram_id, text="Arizangiz yakunlandi. Adminning javobini baholang:", reply_markup=inline_buttons.rating_btns(admin['id']))
    else:
        await message.send_copy(chat_id=applicant_telegram_id, reply_markup=reply_buttons.user_chat_btn)
        application_id = int((await state.get_data()).get('application'))
        chat_msg = await db.select_chat_message(application=application_id)
        if chat_msg is None:
            msgs = json.dumps([])
            chat_msg = await db.add_message_to_chat(application=application_id, messages=msgs)
        if message.media_group_id:
            await message.reply('Mediafayllarni alohida yuboring!')
        else:
            messages = json.loads(chat_msg['messages'])
            if message.content_type == 'text':
                messages.append({'author': 'admin', 'type': 'text', 'text': message.html_text})
            elif message.content_type == 'photo':  
                messages.append({'author': 'admin', 'type': 'photo', 'caption': message.html_text, 'photo': message.photo[-1].file_id})
            elif message.content_type == 'video':
                messages.append({'author': 'admin', 'type': 'video', 'caption': message.html_text, 'video': message.video.file_id})
            elif message.content_type == 'document':
                messages.append({'author': 'admin', 'type': 'document', 'caption': message.html_text, 'document': message.document.file_id})
            elif message.content_type == 'voice':
                messages.append({'author': 'admin', 'type': 'audio', 'caption': message.html_text, 'voice': message.voice.file_id,})
            else:
                await message.answer(text="Xabarni <i>text</i>, <i>rasm</i>, <i>video</i>, <i>dokument</i> yoki <i>audio</i> ko'rinishda yuboring")              
            await db.update_chat_message(messages=json.dumps(messages), application=application_id)


@router.message(F.text.startswith('↩️Javob yozish'))
async def user_no_state_handler(message: types.Message, state: FSMContext):
    user = await db.select_user(telegram_id=message.from_user.id)
    application = await db.select_application(applicant=user['id'], status='Jarayonda')
    if application:
        await message.answer('Marhamat, adminga yozishingiz mukin:')
        await state.set_state(UserState.chat)
    else:
        await message.answer('Siz hali ariza bermagansiz!')


@router.message(F.text.startswith('💬Chatni boshlash'))
async def admin_no_state_handler(message: types.Message, state: FSMContext):
    admin = await db.select_admin(telegram_id=message.from_user.id)
    application = await db.select_application(admin=admin['id'], status='Jarayonda')
    applicant = await db.select_user(id=application['applicant'])
    await state.set_state(AdminsState.chat)
    await state.set_data({'applicant': applicant['telegram_id'], 'application': application['id']})
    await message.answer('Arizachiga yozishingiz mumkin:')