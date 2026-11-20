from aiogram import Router, F, types, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import manager_router, main_bot
from base import get_all_factors, get_all_users, get_user_count, inline_url_maker,  inline_query_maker, get_user_by_user_id
import sqlite3
import asyncio
import logging
import os
import uuid
import datetime
import config
        
class BroadcastState(StatesGroup):
    waiting_for_message = State()


def is_admin(user_id: int) -> bool:
    user = get_user_by_user_id(user_id)
    return bool(user) and user[6] == 1


@manager_router.message(F.text.startswith("ارسال پیام همگانی"))
async def ask_broadcast_message(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("✍️ لطفاً متن/عکس/ویدیو پیام خود را ارسال کنید.")
        await state.set_state(BroadcastState.waiting_for_message)

@manager_router.message(BroadcastState.waiting_for_message)
async def send_broadcast(message: types.Message, state: FSMContext, bot):
    await message.reply("پیام شما در صف ارسال قرار گرفت...")
    users = get_all_users()
    success, failed = 0, 0

    for user in users:
        user_id = user[0]
        try:
            if message.text:
                await main_bot.send_message(chat_id=user_id, text=message.text)
            elif message.photo:
                await main_bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                await main_bot.send_video(chat_id=user_id, video=message.video.file_id, caption=message.caption)
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logging.warning("Broadcast to %s failed: %s", user_id, e)
            failed += 1
            continue

    await message.answer(f"✅ پیام همگانی ارسال شد.\n\nموفق: {success} ||| ناموفق: {failed}")
    await state.clear()

@manager_router.message(F.text.startswith("آمار ربات"))
async def send_stats(message: types.Message):
    if is_admin(message.from_user.id):
        users = get_user_count()

        text = f"👥 تعداد کل کاربران: {users}\n\n"

        await message.answer(text)

@manager_router.message(F.text.startswith("لیست کاربران"))
async def list_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    users = get_all_users()
    if not users:
        await main_bot.send_message(chat_id= message.from_user.id, text= "کاربری ثبت نشده است❌")
        return

    for i in users:
        await main_bot.send_message(
            chat_id=message.from_user.id,
            text=f"""👤 نام کاربر: {i[1]} {i[2] or ""}
🆔 آیدی کاربر: {i[0]}
🎖 یوزرنیم کاربر: {i[5] or "ندارد"}
💰 موجودی کاربر: {i[7]} تومان"""
        )
        await asyncio.sleep(0.1)

@manager_router.message(F.text.startswith("فاکتور های کاربران"))
async def list_factors(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    factors = get_all_factors()
    if not factors:
        await main_bot.send_message(chat_id= message.from_user.id, text= "فاکتوری ثبت نشده است❌")
        return

    for i in factors:
        await main_bot.send_message(chat_id= message.from_user.id, text= f"""🆔کد فاکتور: {i[0]}
👤آیدی کاربر: {i[1]}
🎖یوزرنیم کاربر: {i[2] if i[2] is not None else "ندارد"}
📦نوع اشتراک: {i[3]}
💰مبلغ: {i[4]} تومان
🗓تاریخ ایجاد: {i[5]}
📋وضعیت: {i[6]}""")

        await asyncio.sleep(0.1)
