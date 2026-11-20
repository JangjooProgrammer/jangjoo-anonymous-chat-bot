
from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

ages = list(range(9, 101))

provinces = [
    "آذربایجان شرقی",
    "آذربایجان غربی",
    "اردبیل",
    "اصفهان",
    "البرز",
    "ایلام",
    "بوشهر",
    "تهران",
    "چهارمحال و بختیاری",
    "خراسان جنوبی",
    "خراسان رضوی",
    "خراسان شمالی",
    "خوزستان",
    "زنجان",
    "سمنان",
    "سیستان و بلوچستان",
    "فارس",
    "قزوین",
    "قم",
    "کردستان",
    "کرمان",
    "کرمانشاه",
    "کهگیلویه و بویراحمد",
    "گلستان",
    "گیلان",
    "لرستان",
    "مازندران",
    "مرکزی",
    "هرمزگان",
    "همدان",
    "یزد"
]


def manager_menu():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="آمار ربات 📊"), types.KeyboardButton(text="ارسال پیام همگانی 📢")],
            [types.KeyboardButton(text="لیست کاربران 👥"), types.KeyboardButton(text="فاکتور های کاربران 📄")]
        ],
        resize_keyboard=True
    )
    return keyboard


def user_menu():
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="پشتیبانی 📞"), types.KeyboardButton(text="جست و جو ناشناس 🔍")],
            [types.KeyboardButton(text="خرید سکه 🪙"), types.KeyboardButton(text="حساب کاربری من 🔗")],
            [types.KeyboardButton(text="آموزش استفاده از ربات"), types.KeyboardButton(text="کیف پول 💵")],
        ],
        resize_keyboard=True
    )
    return keyboard


def inline_url_maker(list1, list2):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=name, url=callback)]
        for name, callback in zip(list1, list2)
    ])
    return keyboard


def inline_query_maker(list1, list2):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=name, callback_data=callback)]
        for name, callback in zip(list1, list2)
    ])
    return keyboard


def get_all_users():
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute("SELECT * FROM accounts")
    result = cu.fetchall()

    db.close()
    return result


def get_user_count():
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute("SELECT COUNT(*) FROM accounts")
    result = cu.fetchone()[0]

    db.close()
    return result


def insert_factor(data: tuple):
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute(
        "INSERT INTO factors (id, username, price, time, service, baseinfo, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
        data
    )

    db.commit()
    db.close()


def get_factor_by_id(id: int):
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute("SELECT * FROM factors WHERE id = ?", (id,))
    result = cu.fetchone()

    db.close()
    return result


def update_user_balance(user_id: int, new_balance: int):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute(
        "UPDATE accounts SET balance = ? WHERE id = ?",
        (new_balance, user_id)
    )

    conn.commit()
    conn.close()


def get_balance_by_user_id(user_id: int) -> int:
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute(
        "SELECT balance FROM accounts WHERE id = ?",
        (user_id,)
    )

    result = cu.fetchone()

    db.close()
    return result[0] if result else 0


def separate_by_commas(number_str: str) -> str:
    if not number_str.isdigit():
        if number_str.startswith("-"):
            number_str = number_str.split("-")[1]
            return "-" + "{:,}".format(int(number_str))

    return "{:,}".format(int(number_str))


def age_keyboard():
    builder = ReplyKeyboardBuilder()

    for age in ages:
        builder.button(text=str(age))

    builder.adjust(6)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_all_factors():
    import sqlite3

    db = sqlite3.connect("case.db")
    cu = db.cursor()

    cu.execute("SELECT * FROM factors")
    result = cu.fetchall()

    db.close()
    return result


def province_keyboard():
    builder = ReplyKeyboardBuilder()

    for province in provinces:
        builder.button(text=province)

    builder.adjust(2)

    return builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_user_by_user_id(user_id: int):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (user_id,)
    )

    result = cu.fetchone()

    conn.close()
    return result


def get_admin_id():
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute("SELECT id FROM accounts WHERE admin = 1")
    result = cu.fetchone()

    conn.close()
    return result


def insertinto_accounts(data: tuple):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute("""
        INSERT OR IGNORE INTO accounts
        (id, name, display_name, age, city, username, admin, balance)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, data)

    conn.commit()
    conn.close()

    return "T"


def get_coin_data(user_id):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute(
        "SELECT balance, coins FROM accounts WHERE id = ?",
        (user_id,)
    )

    result = cu.fetchone()

    conn.close()
    return result


def purchase_coins(user_id, coins, price):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    try:
        cu.execute("BEGIN IMMEDIATE")

        cu.execute(
            "SELECT balance FROM accounts WHERE id = ?",
            (user_id,)
        )

        user = cu.fetchone()

        if user is None:
            conn.rollback()
            return False, "حساب کاربری شما پیدا نشد❌"

        if user[0] < price:
            conn.rollback()
            return False, "موجودی کیف پول شما کافی نیست❌"

        cu.execute("""
            UPDATE accounts
            SET balance = balance - ?,
                coins = COALESCE(coins, 0) + ?
            WHERE id = ? AND balance >= ?
        """, (price, coins, user_id, price))

        if cu.rowcount != 1:
            conn.rollback()
            return False, "خرید انجام نشد. دوباره تلاش کنید❌"

        cu.execute("""
            INSERT INTO coin_transactions
            (user_id, coins, price)
            VALUES (?, ?, ?)
        """, (user_id, coins, price))

        cu.execute(
            "SELECT balance, coins FROM accounts WHERE id = ?",
            (user_id,)
        )

        result = cu.fetchone()

        conn.commit()
        return True, result

    except sqlite3.Error:
        conn.rollback()
        return False, "خطا در ثبت خرید رخ داد❌"

    finally:
        conn.close()


def search_and_connect(user_id: int):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    try:
        cu.execute("BEGIN IMMEDIATE")

        cu.execute(
            "SELECT id, coins FROM accounts WHERE id = ?",
            (user_id,)
        )

        user = cu.fetchone()

        if user is None:
            conn.rollback()
            return "not_found", None

        cu.execute("""
            SELECT user1_id, user2_id
            FROM connections
            WHERE status = 'active'
            AND (user1_id = ? OR user2_id = ?)
        """, (user_id, user_id))

        active_connection = cu.fetchone()

        if active_connection:
            partner_id = (
                active_connection[1]
                if active_connection[0] == user_id
                else active_connection[0]
            )

            conn.rollback()
            return "connected", partner_id

        cu.execute(
            "SELECT user_id FROM search_queue WHERE user_id = ?",
            (user_id,)
        )

        if cu.fetchone():
            conn.rollback()
            return "already_searching", None

        if user[1] is None or user[1] < 2:
            conn.rollback()
            return "low_coins", None

        cu.execute("""
            SELECT q.user_id
            FROM search_queue AS q
            INNER JOIN accounts AS a ON a.id = q.user_id
            WHERE q.user_id != ?
            AND COALESCE(a.coins, 0) >= 2
            AND NOT EXISTS (
                SELECT 1
                FROM connections AS c
                WHERE c.status = 'active'
                AND (
                    c.user1_id = q.user_id
                    OR c.user2_id = q.user_id
                )
            )
            ORDER BY RANDOM()
            LIMIT 1
        """, (user_id,))

        waiting_user = cu.fetchone()

        if waiting_user:
            partner_id = waiting_user[0]

            cu.execute(
                "DELETE FROM search_queue WHERE user_id = ?",
                (partner_id,)
            )

            cu.execute("""
                INSERT INTO connections (user1_id, user2_id)
                VALUES (?, ?)
            """, (user_id, partner_id))

            conn.commit()
            return "connected_now", partner_id

        cu.execute(
            "INSERT INTO search_queue (user_id) VALUES (?)",
            (user_id,)
        )

        conn.commit()
        return "waiting", None

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        conn.close()


def remove_from_search_queue(user_id: int):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute(
        "DELETE FROM search_queue WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()


def get_active_connection(user_id: int):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute("""
        SELECT id, user1_id, user2_id
        FROM connections
        WHERE status = 'active'
        AND (user1_id = ? OR user2_id = ?)
        ORDER BY id DESC
        LIMIT 1
    """, (user_id, user_id))

    result = cu.fetchone()
    conn.close()

    if not result:
        return None

    connection_id, user1_id, user2_id = result
    partner_id = user2_id if user1_id == user_id else user1_id

    return {
        "connection_id": connection_id,
        "partner_id": partner_id
    }


def end_connection(user_id: int):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    try:
        cu.execute("BEGIN IMMEDIATE")

        cu.execute("""
            SELECT id, user1_id, user2_id
            FROM connections
            WHERE status = 'active'
            AND (user1_id = ? OR user2_id = ?)
            ORDER BY id DESC
            LIMIT 1
        """, (user_id, user_id))

        connection = cu.fetchone()

        if not connection:
            conn.rollback()
            return None

        connection_id, user1_id, user2_id = connection
        partner_id = user2_id if user1_id == user_id else user1_id

        cu.execute("""
            UPDATE connections
            SET status = 'ended',
                ended_at = CURRENT_TIMESTAMP
            WHERE id = ? AND status = 'active'
        """, (connection_id,))

        cu.execute(
            "DELETE FROM search_queue WHERE user_id IN (?, ?)",
            (user_id, partner_id)
        )

        conn.commit()

        return {
            "connection_id": connection_id,
            "partner_id": partner_id
        }

    except sqlite3.Error:
        conn.rollback()
        raise

    finally:
        conn.close()


def get_public_profile(user_id: int):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute("""
        SELECT display_name, age, city, profile_photo_id
        FROM accounts
        WHERE id = ?
    """, (user_id,))

    result = cu.fetchone()
    conn.close()

    return result


def update_profile_photo(user_id: int, file_id: str):
    import sqlite3

    conn = sqlite3.connect("case.db")
    cu = conn.cursor()

    cu.execute("""
        UPDATE accounts
        SET profile_photo_id = ?
        WHERE id = ?
    """, (file_id, user_id))

    updated = cu.rowcount == 1
    conn.commit()
    conn.close()

    return updated
