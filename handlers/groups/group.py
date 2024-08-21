from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.session.middlewares.request_logging import logger
from loader import db, bot
from data.config import ADMINS
from utils.extra_datas import make_title
from aiogram.fsm.context import FSMContext
import json
from states.test import AdminsState, UserState
from keyboards.reply import buttons as reply_buttons
from keyboards.inline import buttons as inline_buttons
from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove



router = Router()

@router.callback_query()
async def get_app(call: types.CallbackQuery, state: FSMContext):
    if call.data.startswith('accept'):
        admin = await db.select_admin(telegram_id=call.from_user.id)
        if admin:
            _, app_id = call.data.split('_')
            admin_apps = await db.select_application(admin=admin['id'], status='Jarayonda')
            if admin_apps is None:
                application = await db.select_application(id=int(app_id))
                user = await db.select_user(id=application['applicant'])
                await bot.send_message(chat_id=user['telegram_id'], text=f"Sizning <b>{application['created'].strftime('%d.%m.%Y %H:%M')}</b> da bergan arizangiz ko'rib chiqilmoqda...")
                await db.update_application_status('Jarayonda', admin['id'], int(app_id))
                messages = json.loads(application['files'])
                text = f'<b>📥 #{application["id"]} raqamli ariza qabul qilindi</b>\n<b>👤Arizachi:</b> <a href="tg://user?id={user["telegram_id"]}">{user["full_name"]}</a>'
                await bot.send_message(chat_id=admin['telegram_id'], text=text, reply_markup=reply_buttons.end_app)
                for message in messages:
                    if message.get('type') == 'text':
                        await bot.send_message(chat_id=admin['telegram_id'], text=message.get('text'))
                    if message.get('type') == 'photo':
                        await bot.send_photo(chat_id=admin['telegram_id'], photo=message.get('photo'), caption=message.get('caption'))
                    if message.get('type') == 'video':
                        await bot.send_video(chat_id=admin['telegram_id'], video=message.get('video'), caption=message.get('caption'))
                    if message.get('type') == 'document':
                        await bot.send_document(chat_id=admin['telegram_id'], document=message.get('document'), caption=message.get('caption'))
                    if message.get('type') == 'audio':
                        await bot.send_audio(chat_id=admin['telegram_id'], audio=message.get('audio'), caption=message.get('caption'))
                msg_text = call.message.html_text
                new_text = msg_text[:-21] + f'<b>👨🏻‍💻Qabul qildi:</b> <a href="tg://user?id={call.from_user.id}">{admin["full_name"]}</a>\n' + "<b>🎗Status:</b> Jarayonda"
                await call.message.edit_text(text=new_text, reply_markup=None)
            else:
                await call.answer('Siz oldin jarayondagi arizani yakunlashingiz kerak')
        else:
            await call.answer('Siz oldin Admin bo`lishingiz kerak!')

    if call.data.startswith('decline'):
        admin = await db.select_admin(telegram_id=call.from_user.id)
        if admin:
            _, app_id = call.data.split('_')
            admin_apps = await db.select_application(admin=admin['id'], status='Jarayonda')
            if admin_apps is None:
                application = await db.select_application(id=int(app_id))
                user = await db.select_user(id=application['applicant'])
                await bot.send_message(chat_id=user['telegram_id'], text=f"Sizning <b>{application['created'].strftime('%d.%m.%Y %H:%M')}</b> da bergan arizangiz bekor qilindi!")
                await db.update_application_status('Bekor qilingan', admin['id'], int(app_id))
                msg_text = call.message.html_text
                new_text = msg_text[:-21] + f'<b>👨🏻‍💻Qabul qildi:</b> <a href="tg://user?id={call.from_user.id}">{admin["full_name"]}</a>\n' + "<b>🎗Status:</b> Bekor qilingan"
                await call.message.edit_text(text=new_text, reply_markup=None)
            else:
                await call.answer('Siz oldin jarayondagi arizani yakunlashingiz kerak')
        else:
            await call.answer('Siz oldin Admin bo`lishingiz kerak!')


    if call.data.startswith('rating'):
        _, number, admin_id = call.data.split('_')
        number = int(number)
        admin_id = int(admin_id)
        await call.message.delete()
        await call.message.answer(f'Baho uchun raxmat!\n\nYana qanday yordam bera olaman?', reply_markup=reply_buttons.main_markup)
        admin = await db.select_admin(id=admin_id)
        await db.update_admin_stars(admin['rating'] + number, admin_id)
        await state.set_state(UserState.main)

    
    await call.answer()