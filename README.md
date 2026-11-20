# 🥷 Jangjoo Anonymous Chat Bot

**English** · [فارسی](README.fa.md)

An anonymous Telegram chat bot with a **wallet**, a **coin shop** and an **admin panel**. This is a personal project, built to show off Telegram bot development skills.

🤖 **Try the bot:** @Jangjoo_chat_bot

## ✨ Features

### For users

* Sign-up with display name, age, city and profile photo
* Anonymous search with a waiting queue that pairs two users together
* View the other user's public profile and end the connection
* Wallet: pick a preset or custom amount (minimum 25,000 Toman), send a receipt photo, and an admin approves it
* Coin shop with four packages (100, 250, 600 and 1500 coins) paid from the wallet balance; the deduction and the coin credit happen in a single database transaction
* Starting an anonymous search costs coins
* Help and support sections

### For admins

* Total user statistics
* User and invoice lists
* Approve or reject wallet top-up receipts (inline buttons)
* Broadcast messages (text, photo and video)

## 🛠 Tech stack

Python • aiogram 3 • SQLite • FSM • asyncio • python-dotenv

## 📁 Project structure

| File | Responsibility |
|-|-|
|`main.py`|Bot entry point and the `/start` command|
|`config.py`|Settings from `.env`, bot and router setup|
|`database.py`|Creates the SQLite tables and registers the admin account|
|`base.py`|Database helpers and keyboard builders|
|`accounting.py`|Sign-up and user account|
|`connection.py`|Anonymous search and chat|
|`balance.py`|Wallet and receipt approval|
|`coins.py`|Coin shop|
|`manage.py`|Admin panel|
|`help.py` and `support.py`|Help and support|

## 💳 About payments

Wallet top-ups are **card-to-card**: the user sends a receipt and an admin approves it. There is no online payment gateway, but the project is structured so one (for example Zarinpal) can be added later.

## 🚀 Running the bot

The project is developed with Python 3.14.

```bash
git clone https://github.com/JangjooProgrammer/jangjoo-anonymous-chat-bot.git
cd jangjoo-anonymous-chat-bot

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example`, rename it to `.env`, then fill in the values:

```env
BOT_TOKEN=bot token from BotFather
ADMIN_ID=admin's numeric Telegram ID
ADMIN_USERNAME=admin username
PAYMENT_CARDS=card numbers, comma separated
CARD_OWNER=name on the card
SUPPORT_USERNAME=support username
```

```bash
python main.py
```

The database tables and the admin account are created automatically on the first run.

## 🔒 Security notes

* `.env`, the database (`case.db`) and log files are never committed to git.
* The token, card numbers and admin ID are read only from `.env`.
