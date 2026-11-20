from aiogram import types, filters, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm import state

from config import coin_router, main_bot
from base import (
    get_user_by_user_id,
    inline_query_maker,
    separate_by_commas,
    get_coin_data,
    purchase_coins
)


class BuyCoins(state.StatesGroup):
    selecting = state.State()
    confirming = state.State()


COIN_PACKAGES = {
    "1": {"coins": 100, "price": 50000},
    "2": {"coins": 250, "price": 100000},
    "3": {"coins": 600, "price": 200000},
    "4": {"coins": 1500, "price": 400000}
}


@coin_router.message(F.text == "خرید سکه 🪙")
async def coins_menu(message: types.Message, state: FSMContext):
    user = get_user_by_user_id(message.from_user.id)

    if user is None:
        await message.reply(
            text="متاسفانه شما هنوز حساب کاربری ندارید💤"
        )
        return

    account = get_coin_data(message.from_user.id)

    if account is None:
        await message.reply(text="اطلاعات حساب شما پیدا نشد❌")
        return

    balance, coins = account

    text = f"""<b>🪙 فروشگاه سکه جنگجو</b>

💰 اعتبار کیف پول: {separate_by_commas(str(balance))} تومان
🪙 موجودی سکه: {separate_by_commas(str(coins))}

لطفاً یکی از بسته‌های زیر را انتخاب کنید:"""

    keyboard = inline_query_maker(
        [
            "100 سکه | 50,000 تومان",
            "250 سکه | 100,000 تومان",
            "600 سکه | 200,000 تومان",
            "1500 سکه | 400,000 تومان",
            "انصراف"
        ],
        [
            "coin:1",
            "coin:2",
            "coin:3",
            "coin:4",
            "coin:cancel"
        ]
    )

    await main_bot.send_message(
        chat_id=message.from_user.id,
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    await state.set_state(BuyCoins.selecting)


@coin_router.callback_query(
    filters.StateFilter(BuyCoins.selecting),
    F.data.in_({"coin:1", "coin:2", "coin:3", "coin:4", "coin:cancel"})
)
async def select_coin_package(query: types.CallbackQuery, state: FSMContext):
    if query.data == "coin:cancel":
        await query.message.edit_text(
            "شما از خرید سکه منصرف شدید🏠"
        )
        await state.clear()
        await query.answer()
        return

    package_id = query.data.split(":")[1]
    package = COIN_PACKAGES.get(package_id)

    if package is None:
        await query.answer(
            "بسته انتخاب‌شده معتبر نیست❌",
            show_alert=True
        )
        return

    account = get_coin_data(query.from_user.id)

    if account is None:
        await query.answer(
            "حساب کاربری شما پیدا نشد❌",
            show_alert=True
        )
        return

    balance, coins = account

    await state.update_data(package_id=package_id)
    await state.set_state(BuyCoins.confirming)

    text = f"""<b>🧾 فاکتور خرید سکه</b>

🪙 تعداد سکه: {separate_by_commas(str(package['coins']))}
💰 مبلغ پرداختی: {separate_by_commas(str(package['price']))} تومان

💳 موجودی کیف پول شما: {separate_by_commas(str(balance))} تومان

آیا خرید این بسته را تأیید می‌کنید؟"""

    keyboard = inline_query_maker(
        ["تأیید خرید✅", "بازگشت🔙", "انصراف"],
        ["coin:confirm", "coin:back", "coin:cancel"]
    )

    await query.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    await query.answer()


@coin_router.callback_query(
    filters.StateFilter(BuyCoins.confirming),
    F.data == "coin:back"
)
async def back_to_coin_packages(query: types.CallbackQuery, state: FSMContext):
    account = get_coin_data(query.from_user.id)

    if account is None:
        await query.answer(
            "حساب کاربری شما پیدا نشد❌",
            show_alert=True
        )
        return

    balance, coins = account

    text = f"""<b>🪙 فروشگاه سکه جنگجو</b>

💰 اعتبار کیف پول: {separate_by_commas(str(balance))} تومان
🪙 موجودی سکه: {separate_by_commas(str(coins))}

لطفاً یکی از بسته‌های زیر را انتخاب کنید:"""

    keyboard = inline_query_maker(
        [
            "100 سکه | 50,000 تومان",
            "250 سکه | 100,000 تومان",
            "600 سکه | 200,000 تومان",
            "1500 سکه | 400,000 تومان",
            "انصراف"
        ],
        [
            "coin:1",
            "coin:2",
            "coin:3",
            "coin:4",
            "coin:cancel"
        ]
    )

    await query.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    await state.set_state(BuyCoins.selecting)
    await query.answer()


@coin_router.callback_query(
    filters.StateFilter(BuyCoins.confirming),
    F.data == "coin:cancel"
)
async def cancel_coin_purchase(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_text(
        "شما از خرید سکه منصرف شدید🏠"
    )

    await state.clear()
    await query.answer()


@coin_router.callback_query(
    filters.StateFilter(BuyCoins.confirming),
    F.data == "coin:confirm"
)
async def confirm_coin_purchase(query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    package_id = data.get("package_id")

    package = COIN_PACKAGES.get(package_id)

    if package is None:
        await query.answer(
            "اطلاعات خرید معتبر نیست❌",
            show_alert=True
        )
        await state.clear()
        return

    success, result = purchase_coins(
        query.from_user.id,
        package["coins"],
        package["price"]
    )

    if not success:
        await query.answer(result, show_alert=True)
        return

    balance, coins = result

    text = f"""<b>خرید شما با موفقیت انجام شد✅</b>

🪙 سکه دریافت‌شده: {separate_by_commas(str(package['coins']))}
💰 مبلغ پرداخت‌شده: {separate_by_commas(str(package['price']))} تومان

🪙 موجودی فعلی سکه: {separate_by_commas(str(coins))}
💳 موجودی باقی‌مانده کیف پول: {separate_by_commas(str(balance))} تومان"""

    await query.message.edit_text(
        text=text,
        parse_mode="HTML"
    )

    await state.clear()
    await query.answer("خرید با موفقیت انجام شد✅")
