from aiogram import types, filters, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm import state
from config import connection_router, main_bot
import logging
from base import (
    get_user_by_user_id,
    inline_query_maker,
    search_and_connect,
    remove_from_search_queue,
    get_active_connection,
    end_connection,
    get_public_profile,
)

import logging

logger = logging.getLogger("connection")

handler = logging.FileHandler("connection.log", encoding="utf-8")
handler.setLevel(logging.INFO)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.propagate = False

class ConnectionStates(state.StatesGroup):
    searching = state.State()

def active_chat_keyboard():
    return inline_query_maker(
        ["مشاهده پروفایل کاربر 👤", "قطع اتصال ❌"],
        ["connection:profile", "connection:disconnect"]
    )


async def send_connected_message(chat_id: int, text: str):
    await main_bot.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=active_chat_keyboard()
    )


@connection_router.message(F.text == "جست و جو ناشناس 🔍")
async def connection_menu(message: types.Message, state: FSMContext):
    user = get_user_by_user_id(message.from_user.id)

    if user is None:
        await message.reply("متاسفانه شما هنوز حساب کاربری ندارید💤")
        return

    active = get_active_connection(message.from_user.id)

    if active:
        await message.answer(
            "شما هم‌اکنون به یک کاربر متصل هستید.",
            reply_markup=active_chat_keyboard()
        )
        return

    text = """<b>🔍 جست و جو ناشناس</b>

برای شروع جست و جو، لطفاً روی دکمه زیر کلیک کنید. پس از آن، شما به صورت ناشناس به یک کاربر دیگر متصل خواهید شد و می‌توانید با او گفتگو کنید."""

    keyboard = inline_query_maker(
        ["شروع جست و جو 🔎", "انصراف"],
        ["connection:start", "connection:cancel"]
    )

    await state.set_state(ConnectionStates.searching)

    await message.answer(
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@connection_router.callback_query(
    filters.StateFilter(ConnectionStates.searching),
    F.data == "connection:start"
)
async def start_search(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    result, partner_id = search_and_connect(user_id)

    if result == "not_found":
        await callback.message.edit_text("شما حساب کاربری ندارید.")
        await state.clear()

    elif result == "low_coins":
        await callback.message.edit_text(
            "❌ تعداد سکه‌های شما برای شروع جست‌وجو کافی نیست.\n\n"
            "برای استفاده از چت ناشناس حداقل به ۲ سکه نیاز دارید.\n\n"
            "ابتدا کیف پول خود را شارژ کنید و سپس از بخش خرید سکه، سکه تهیه کنید."
        )
        await state.clear()

    elif result == "connected":
        await callback.message.edit_text("شما در حال حاضر به یک کاربر متصل هستید.")
        await state.clear()

    elif result == "already_searching":
        await callback.message.edit_text(
            "شما در حال حاضر در صف جست‌وجو هستید.",
            reply_markup=inline_query_maker(["انصراف"], ["connection:cancel"])
        )

    elif result == "waiting":
        await callback.message.edit_text(
            "🔍 جست‌وجو برای پیدا کردن یک کاربر آغاز شد...\n\nلطفاً منتظر بمانید.",
            reply_markup=inline_query_maker(["انصراف"], ["connection:cancel"])
        )

    elif result == "connected_now":
        await callback.message.edit_text(
            "✅ یک کاربر پیدا شد! شما اکنون به هم متصل شدید.",
            reply_markup=active_chat_keyboard()
        )

        await send_connected_message(
            partner_id,
            "✅ یک کاربر پیدا شد! شما اکنون به هم متصل شدید."
        )

        await state.clear()

    await callback.answer()


@connection_router.callback_query(
    filters.StateFilter(ConnectionStates.searching),
    F.data == "connection:cancel"
)
async def cancel_search(callback: types.CallbackQuery, state: FSMContext):
    remove_from_search_queue(callback.from_user.id)
    await callback.message.edit_text("جست‌وجو لغو شد.")
    await state.clear()
    await callback.answer()


@connection_router.callback_query(F.data == "connection:profile")
async def show_partner_profile(callback: types.CallbackQuery):
    active = get_active_connection(callback.from_user.id)

    if not active:
        await callback.answer("اتصال فعالی ندارید.", show_alert=True)
        return

    profile = get_public_profile(active["partner_id"])

    if not profile:
        await callback.answer("اطلاعات پروفایل پیدا نشد.", show_alert=True)
        return

    display_name, age, city, photo_id = profile

    text = (
        "👤 پروفایل کاربر مقابل\n\n"
        f"نام نمایشی: {display_name or 'ثبت نشده'}\n"
        f"سن: {age if age is not None else 'ثبت نشده'}\n"
        f"استان: {city or 'ثبت نشده'}"
    )

    if photo_id:
        await main_bot.send_photo(
            chat_id=callback.from_user.id,
            photo=photo_id,
            caption=text
        )
    else:
        await main_bot.send_message(
            chat_id=callback.from_user.id,
            text=text
        )

    await callback.answer()


@connection_router.callback_query(F.data == "connection:disconnect")
async def disconnect_chat(callback: types.CallbackQuery, state: FSMContext):
    result = end_connection(callback.from_user.id)

    if not result:
        await callback.message.edit_text("اتصال فعالی برای قطع کردن وجود ندارد.")
        await state.clear()
        await callback.answer()
        return

    partner_id = result["partner_id"]

    await callback.message.edit_text("❌ اتصال شما با موفقیت قطع شد.")
    await state.clear()

    try:
        await main_bot.send_message(
            chat_id=partner_id,
            text="❌ کاربر مقابل اتصال را قطع کرد. گفتگو پایان یافت."
        )
    except Exception:
        pass

    await callback.answer("اتصال برای هر دو طرف قطع شد.")


# پیام‌های کاربران فقط در صورت وجود اتصال فعال به طرف مقابل منتقل می‌شوند.
@connection_router.message()
async def relay_chat_messages(message: types.Message):
    if message.from_user is None:
        return

    active = get_active_connection(message.from_user.id)

    if not active:
        return

    # پیام‌های فرمان‌دار و دکمه‌های منوی اصلی به‌عنوان پیام چت منتقل نمی‌شوند.
    if message.text and message.text.startswith("/"):
        return

    try:
        await main_bot.copy_message(
            chat_id=active["partner_id"],
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=active_chat_keyboard()
        )
    except Exception:
        await message.answer("ارسال پیام انجام نشد. لطفاً دوباره تلاش کنید.")


@connection_router.edited_message()
async def ignore_edited_messages(message: types.Message):
    return
