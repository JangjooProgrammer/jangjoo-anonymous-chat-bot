from aiogram import F,types
from base import inline_url_maker
from config import support_router, SUPPORT_USERNAME
    
@support_router.message(F.text.startswith("پشتیبانی"))
async def support(message: types.Message):
    await message.reply(text= f"""
🛠 نکات مهم در مورد پیام دادن به پشتیبانی :

💥1. موقع پیام دادن مشکل خودتون رو به صورت فارسی تایپ کنید (انگلیسی یا ویس نفرستید)

💥2. حتما اسم اینترنت، سیستم عامل (اندروید، آیفون، ویندوز) و برنامه ای که ازش استفاده میکنید رو بگید

💥3.  ترتیب پاسخگویی از پیام های قدیمی تر به جدید هست، یعنی اگر در زمان های مختلف پیام جدید بدید فقط نوبت پاسخگویی تون رو عقب میندازید

💥4. حتما آموزش های کانال رو با دقت تماشا کنید

⚠️ لطفا قبل از پیام دادن این موارد رو رعایت کنید تا مشکل شما سریع و کامل برطرف شود.

👨‍💻 پشتیبانی = @{SUPPORT_USERNAME}

""", reply_markup= inline_url_maker(["انتقال به پشتیبانی👨‍💻"], [f"https://t.me/{SUPPORT_USERNAME}"]))