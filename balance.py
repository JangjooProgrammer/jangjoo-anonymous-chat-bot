from aiogram import types, filters, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm import state
import logging
from config import balance_router, main_bot, PAYMENT_CARDS, CARD_OWNER
from base import get_user_by_user_id, inline_query_maker, update_user_balance, get_balance_by_user_id, get_admin_id, separate_by_commas

import logging

logger = logging.getLogger("balance")

handler = logging.FileHandler("balance.log", encoding="utf-8")
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False

def invoice_text() -> str:
    cards = "\n\n".join(f"<blockquote><code>{c}</code></blockquote>" for c in PAYMENT_CARDS)
    return f"""<b>✅فاکتور شارژ حساب کاربری</b>

شماره کارت‌های پرداخت :

{cards}
👤 صاحب کارت: {CARD_OWNER}

برای تأیید پرداخت، عکس رسید خود را ارسال کنید. بعد از پرداخت و تأیید تراکنش، مبلغ مورد نظر به حساب شما اضافه می‌شود!

مبلغ را بصورت دقیق پرداخت کنید، درصورت واریز اشتباه امکان بازگشت وجه وجود ندارد !"""


class UpdateBalance(state.StatesGroup):
    adding = state.State()
    waiting_for_receipt = state.State()
    waiting_for_user_price = state.State()
    waiting_for_admin_approval = state.State()
    premium = state.State()
    
@balance_router.message(F.text.startswith("کیف پول"))
async def balance(message: types.Message):
    if get_user_by_user_id(message.from_user.id) == None:
        await message.reply(text= "متاسفانه شما هنوز حساب کاربری ندارید💤")
    else:
        
        user = get_user_by_user_id(message.from_user.id)
        mess = f"""<b>Rocket🗝</b>
✅ اطلاعات حساب شما:

💬 نام کاربری: @{user[5]}
📲 شناسه کاربری: {user[0]}
💲 اعتبار در دسترس: {separate_by_commas(str(user[7]))} تومان
~~~~~~~~~~~~~~~~~~~~

    برای افزایش موجودی از گزینه‌های زیر استفاده کنید 😄"""
        await main_bot.send_message(chat_id= message.from_user.id, text= mess,
        reply_markup= inline_query_maker(["افزایش موجودی💵", "انصراف"], ["optyes", "optcancel"]), parse_mode= "HTML")
    
@balance_router.callback_query(F.data.startswith("opt"))
async def choice(query: types.CallbackQuery, state: FSMContext):
    if query.data == "optyes":
        key = inline_query_maker(["30,000 تومان", "50,000 تومان", "75,000 تومان", "100,000 تومان", "200,000 تومان", "300,000 تومان", "افزایش به مبلغ دلخواه💸", "انصراف"], ["30000", "50000", "75000", "100000", "200000", "300000", "add", "cancel"])
        await main_bot.edit_message_reply_markup(chat_id= query.from_user.id, message_id= query.message.message_id, reply_markup= key)
        await state.set_state(UpdateBalance.adding)
    elif query.data == "optcancel":
        await main_bot.send_message(chat_id= query.from_user.id, text= "شما اکنون در صفحه اصلی قرار دارید🏠")
        await state.clear()

@balance_router.callback_query(filters.StateFilter(UpdateBalance.adding))
async def update_balance(query: types.CallbackQuery, state: FSMContext):
    if query.data.isdigit():
        await state.update_data(price = query.data)
        await main_bot.send_message(chat_id= query.from_user.id, text= invoice_text(), parse_mode= "HTML")
        await state.set_state(UpdateBalance.waiting_for_receipt)
    if query.data == "add":
        await main_bot.send_message(chat_id= query.from_user.id, text= "لطفا مبلغ مورد نظر را عددی(انگلیسی و بدون فاصله) وارد کنید:")
        await state.set_state(UpdateBalance.waiting_for_user_price)
    if query.data == "cancel":
        await main_bot.send_message(chat_id= query.from_user.id, text= "شما اکنون در صفحه اصلی قرار دارید🏠")
        await state.clear()
        
@balance_router.message(filters.StateFilter(UpdateBalance.waiting_for_user_price))
async def user_price(message: types.Message, state: FSMContext):
    if message.text.isdigit() == False:
        await message.reply(text= "لطفا فقط عدد وارد کنید👇🏼")
    else:
        if int(message.text) < 25000:
            await message.reply(text= "مبلغ وارد شده کم تر از حد مجاز(25,000T) است، دوباره مبلغ را درست وارد کنید👇🏼")
        else:
            await state.update_data(price = message.text)
            await main_bot.send_message(chat_id= message.from_user.id, text= invoice_text(), parse_mode= "HTML")
            await state.set_state(UpdateBalance.waiting_for_receipt)

@balance_router.message(filters.StateFilter(UpdateBalance.waiting_for_receipt))
async def getting_receipt(message: types.Message, state: FSMContext):
    if message.photo:
        try:
            photo_id = message.photo[-1].file_id
            user = get_user_by_user_id(message.from_user.id)
            managerID = get_admin_id()[0]
            data = await state.get_data()
            await main_bot.send_photo(chat_id= managerID, photo= photo_id, caption= f"فیش واریزی {user[5]} را تایید یا رد کنید👇🏼({data.get('price')}T)", reply_markup= inline_query_maker(["تایید✅", "رد❌"], [f"1admin:{message.from_user.id}:{data.get('price')}", f"0admin:{message.from_user.id}"]))
            await message.reply(text= "برای ادمین ارسال شد✅ تا حداکثر سه ساعت دیگه وضعیت مشخص می شود🕧")
            await state.clear()
        except Exception as e:
            await message.reply(text= "به مشکل برخورد❌")
            await state.clear()
    else:
        await message.reply(text= "تایید نشد❌ ")
        await main_bot.send_message(chat_id= message.from_user.id, text= "شما اکنون در صفحه اصلی قرار دارید")
        await state.clear()
    
@balance_router.callback_query(F.data.find("admin") != -1)
async def handle_admin_decision(query: types.CallbackQuery):
    data = query.data

    admin = get_admin_id()
    if not admin or query.from_user.id != admin[0]:
        await query.answer("دسترسی ندارید", show_alert=True)
        return

    if data.startswith("1admin:"):
        try:
            _, user_id, price = data.split(":")
            user_id = int(user_id)
            price = int(price)

            # آپدیت موجودی کاربر
            current_balance = int(get_balance_by_user_id(user_id))
            update_user_balance(user_id, current_balance + price)

            await main_bot.send_message(chat_id=user_id, text="رسید شما توسط مدیر تایید شد ✅")
            await query.message.edit_reply_markup(reply_markup=None)
            await query.answer("✅ تأیید شد", show_alert=True)
            

        except Exception as e:
            await query.answer("❌ خطا هنگام تایید", show_alert=True)

    elif data.startswith("0admin:"):
        try:
            _, user_id = data.split(":")
            user_id = int(user_id)

            await main_bot.send_message(chat_id=user_id, text="رسید شما توسط مدیر تایید نشد ❌")
            await query.message.edit_reply_markup(reply_markup=None)
            await query.answer("❌ رد شد", show_alert=True)
        except Exception as e:
            await query.answer("❌ خطا هنگام رد", show_alert=True)
            