from aiogram import F, types, filters
from aiogram.fsm.context import FSMContext
from config import main_router, main_bot, dp
from base import manager_menu, user_menu, get_user_by_user_id
from accounting import register_start
import asyncio, logging
import database, base, accounting, help, support, manage, balance, coins, connection

logging.basicConfig(
    filename="log.log",
    level=logging.INFO,
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


@main_router.message(filters.CommandStart())
async def start_bot(message: types.Message, state: FSMContext):
    await message.answer("در حال بررسی اطلاعات شما لطفا صبر کنید...⏳")
    await asyncio.sleep(1)
    if get_user_by_user_id(message.from_user.id):
            if get_user_by_user_id(message.from_user.id)[6] == 1:
                await main_bot.send_message(chat_id= message.from_user.id, text= "به منوی مدیریت ربات خوش آمدید👨‍💻", reply_markup= manager_menu())
                return
            else:
                await message.answer(text= "به ربات چت ناشناس جنگجو خوش آمدید", reply_markup= user_menu())
                
    else:
        await register_start(message, state)
            

async def main():
    await dp.start_polling(main_bot)
    
if __name__ == "__main__":
    asyncio.run(main()) 
    