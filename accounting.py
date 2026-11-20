from aiogram import F, types
from config import account_router
from base import (
    age_keyboard,
    province_keyboard,
    get_user_by_user_id,
    provinces,
    user_menu,
    inline_query_maker,
    update_profile_photo,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import sqlite3
import logging

logger = logging.getLogger("accounting")
logger.setLevel(logging.INFO)

handler = logging.FileHandler("accounting.log", encoding="utf-8")
handler.setFormatter(logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
))

logger.addHandler(handler)


class acount_states(StatesGroup):
    waiting_for_display_name = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_for_profile_photo = State()


async def register_start(message: types.Message, state: FSMContext):
    await state.set_state(acount_states.waiting_for_display_name)
    await message.answer("برای شروع ثبت نام، نام نمایشی خود را وارد کنید:")


@account_router.message(acount_states.waiting_for_display_name)
async def get_display_name(message: types.Message, state: FSMContext):
    if not message.text or not message.text.strip():
        await message.answer("لطفاً یک نام نمایشی معتبر وارد کنید:")
        return

    display_name = message.text.strip()

    if len(display_name) > 55:
        await message.answer("نام نمایشی نباید بیشتر از ۵۵ کاراکتر باشد.")
        return

    await state.update_data(display_name=display_name)
    await state.set_state(acount_states.waiting_for_age)

    await message.answer(
        "نام نمایشی ثبت شد. ✅\n\nحالا سن خود را از کیبورد پایین انتخاب کنید:",
        reply_markup=age_keyboard()
    )


@account_router.message(acount_states.waiting_for_age)
async def get_age(message: types.Message, state: FSMContext):
    if not message.text or not message.text.isdigit():
        await message.answer("لطفاً سن خود را از کیبورد پایین انتخاب کنید.")
        return

    age = int(message.text)

    if age not in range(9, 101):
        await message.answer("سن باید بین ۹ تا ۱۰۰ سال باشد.")
        return

    await state.update_data(age=age)
    await state.set_state(acount_states.waiting_for_city)

    await message.answer(
        "سن ثبت شد. ✅\n\nحالا استان محل سکونت خود را انتخاب کنید:",
        reply_markup=province_keyboard()
    )


@account_router.message(acount_states.waiting_for_city)
async def get_city(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("لطفاً استان محل سکونت خود را انتخاب کنید.")
        return

    city = message.text.strip()

    if city not in provinces:
        await message.answer("لطفاً یکی از استان‌های موجود در کیبورد را انتخاب کنید.")
        return

    data = await state.get_data()
    display_name = data["display_name"]
    age = data["age"]

    user_id = message.from_user.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    conn = None

    try:
        conn = sqlite3.connect("case.db")
        cu = conn.cursor()

        cu.execute("SELECT id FROM accounts WHERE id = ?", (user_id,))

        if cu.fetchone():
            await state.clear()
            await message.answer(
                "حساب کاربری شما از قبل ثبت شده است.",
                reply_markup=user_menu()
            )
            return

        cu.execute("""
            INSERT INTO accounts
            (id, name, display_name, age, city, username, admin, balance, profile_photo_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            full_name,
            display_name,
            age,
            city,
            username,
            0,
            0,
            None
        ))

        conn.commit()
        await state.clear()

        await message.answer(
            "ثبت نام شما با موفقیت انجام شد. 🎉\n\nبه خانواده جنگجو خوش آمدید! ⚔️",
            reply_markup=user_menu()
        )

    except sqlite3.Error as e:
        await message.answer(f"خطا در ذخیره اطلاعات در پایگاه داده:\n{e}")

    finally:
        if conn:
            conn.close()


@account_router.message(F.text.startswith("حساب کاربری من"))
async def show_user_info(message: types.Message):
    user = get_user_by_user_id(message.from_user.id)

    if not user:
        await message.answer("حساب کاربری شما پیدا نشد.")
        return

    if user[6] == 1:
        await message.answer("شما مدیر ربات هستید. 👨‍💻")
        return

    balance = f"{user[7]:,}"
    photo_id = user[9] if len(user) > 9 else None

    mess = f"""<b>Rocket</b>
📘 اطلاعات حساب شما:

👤 نام نمایشی: {user[2]}
🎂 سن: {user[3]}
📍 استان: {user[4]}
💬 نام کاربری تلگرام: @{user[5] if user[5] else 'ندارد'}
📲 شناسه کاربری: {user[0]}
💲 اعتبار در دسترس: {balance} تومان

~~~~~~~~~~~~~~~~~~~~

(برای افزایش موجودی از طریق منوی کیف پول اقدام کنید 💵)
"""

    keyboard = inline_query_maker(
        ["تنظیم عکس پروفایل 🖼"],
        ["account:set_profile_photo"]
    )

    if photo_id:
        await message.answer_photo(
            photo=photo_id,
            caption=mess,
            parse_mode="HTML",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            mess,
            parse_mode="HTML",
            reply_markup=keyboard
        )


@account_router.callback_query(F.data == "account:set_profile_photo")
async def start_profile_photo_setup(callback: types.CallbackQuery, state: FSMContext):
    user = get_user_by_user_id(callback.from_user.id)

    if not user:
        await callback.answer("حساب کاربری پیدا نشد.", show_alert=True)
        return

    await state.set_state(acount_states.waiting_for_profile_photo)
    await callback.message.answer("لطفاً عکس موردنظر برای پروفایل خود را به‌صورت تصویر ارسال کنید.")
    await callback.answer()


@account_router.message(acount_states.waiting_for_profile_photo, F.photo)
async def save_profile_photo(message: types.Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    updated = update_profile_photo(message.from_user.id, photo_id)

    if not updated:
        await message.answer("ذخیره عکس انجام نشد. لطفاً دوباره تلاش کنید.")
        return

    await state.clear()
    await message.answer("✅ عکس پروفایل شما با موفقیت ذخیره شد.")


@account_router.message(acount_states.waiting_for_profile_photo)
async def invalid_profile_photo(message: types.Message):
    await message.answer("لطفاً فقط یک عکس ارسال کنید.")
