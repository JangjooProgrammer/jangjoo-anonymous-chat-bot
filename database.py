import sqlite3
from base import insertinto_accounts
from config import ADMIN_ID, ADMIN_USERNAME

conn = sqlite3.connect("case.db")
cu = conn.cursor()

cu.execute("""
    CREATE TABLE IF NOT EXISTS accounts(
        id INTEGER PRIMARY KEY,
        name VARCHAR(55),
        display_name VARCHAR(55),
        age INTEGER,
        city VARCHAR,
        username VARCHAR(55),
        admin INTEGER,
        balance INTEGER,
        coins INTEGER DEFAULT 0,
        profile_photo_id TEXT
    )
""")

# افزودن ستون به دیتابیس‌های قدیمی، بدون حذف اطلاعات قبلی
cu.execute("PRAGMA table_info(accounts)")
account_columns = [column[1] for column in cu.fetchall()]

if "profile_photo_id" not in account_columns:
    cu.execute("ALTER TABLE accounts ADD COLUMN profile_photo_id TEXT")

cu.execute("""
    CREATE TABLE IF NOT EXISTS factors(
        id TEXT PRIMARY KEY,
        username VARCHAR(55),
        price INTEGER,
        time TEXT,
        service TEXT,
        baseinfo TEXT,
        status TEXT
    )
""")

cu.execute("""
    CREATE TABLE IF NOT EXISTS coin_transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        coins INTEGER NOT NULL,
        price INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cu.execute("""
    CREATE TABLE IF NOT EXISTS search_queue(
        user_id INTEGER PRIMARY KEY,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

cu.execute("""
    CREATE TABLE IF NOT EXISTS connections(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user1_id INTEGER NOT NULL,
        user2_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ended_at TIMESTAMP
    )
""")

cu.execute("""
    CREATE INDEX IF NOT EXISTS idx_connections_users
    ON connections(user1_id, user2_id, status)
""")

conn.commit()
conn.close()

# اگر مدیر از قبل ثبت شده باشد، رکورد تکراری ایجاد نمی‌شود.
insertinto_accounts((ADMIN_ID, "Admin", "Admin", 0, "-", ADMIN_USERNAME, 1, 0))
