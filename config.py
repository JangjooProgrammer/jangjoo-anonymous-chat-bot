import os

from dotenv import load_dotenv
from aiogram import Bot, Router, Dispatcher

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
PAYMENT_CARDS = [c.strip() for c in os.getenv("PAYMENT_CARDS", "").split(",") if c.strip()]
CARD_OWNER = os.getenv("CARD_OWNER", "")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Create a .env file (see .env.example).")

try:
    # aiogram >= 3.7
    from aiogram.client.default import DefaultBotProperties
    main_bot = Bot(BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
except ImportError:
    # aiogram < 3.7
    main_bot = Bot(BOT_TOKEN, parse_mode="HTML")

dp = Dispatcher()

main_router = Router(name= "main_router")
account_router = Router(name= "account_router")
help_router = Router(name= "help_router")
support_router = Router(name= "support_router")
manager_router = Router(name= "manager_router")
balance_router = Router(name= "balance_router")
coin_router = Router(name= "coin_router")
connection_router = Router(name= "connection_router")

dp.include_router(main_router)
dp.include_router(account_router)
dp.include_router(help_router)
dp.include_router(support_router)
dp.include_router(manager_router)
dp.include_router(balance_router)
dp.include_router(coin_router)
dp.include_router(connection_router)