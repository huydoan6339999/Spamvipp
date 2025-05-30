import logging
import time
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from keep_alive import keep_alive

# Khởi động keep alive (nếu chạy trên Replit hoặc host tương tự)
keep_alive()

# Telegram Bot Token
BOT_TOKEN = "6320148381:AAH_ihVyyOGOHOfDU-XFhi0an-tKXdtgL50"
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# Hàm an toàn lấy dữ liệu từ dict
def safe_get(data, key, default="N/A"):
    return data.get(key) if data.get(key) is not None else default

# Hàm lấy số từ chuỗi (nếu API trả về kiểu: "50 likes")
def extract_number(value):
    if not value:
        return "0"
    return "".join(c for c in str(value) if c.isdigit())

@dp.message_handler(commands=["start", "help"])
async def welcome(message: types.Message):
    await message.reply("👋 Chào bạn!\nGửi lệnh:\n<code>/like uid region</code>\n\nVí dụ: <code>/like 123456789 SEA</code>")

@dp.message_handler(commands=["like"])
async def like_handler(message: types.Message):
    args = message.text.strip().split()

    if len(args) != 3:
        await message.reply("❌ Sai cú pháp.\nDùng: <code>/like uid region</code>\nVí dụ: <code>/like 123456789 SEA</code>")
        return

    uid = args[1]
    region = args[2]
    url = f"https://likes-application.vercel.app/like?uid={uid}&region={region}"

    start_time = time.time()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                elapsed = time.time() - start_time
                data = await resp.json()

                if resp.status == 200 and data.get("success"):
                    reply_text = (
                        "<b>BUFF LIKE THÀNH CÔNG ✅</b>\n"
                        f"╭👤 Name: <code>{safe_get(data, 'PlayerNickname')}</code>\n"
                        f"├🆔 UID : <code>{safe_get(data, 'uid')}</code>\n"
                        f"├🌏 Region : <code>{region}</code>\n"
                        f"├📉 Like trước đó: <code>{safe_get(data, 'likes_before')}</code>\n"
                        f"├📈 Like sau khi gửi: <code>{safe_get(data, 'likes_after')}</code>\n"
                        f"╰👍 Like được gửi: <code>{extract_number(data.get('likes_given'))}</code>\n"
                        f"⏱ Thời gian phản hồi: {elapsed:.2f} giây"
                    )
                else:
                    reply_text = f"❌ API trả về lỗi:\n<code>{data}</code>\n⏱ {elapsed:.2f} giây"

                await message.reply(reply_text)
    except Exception as e:
        await message.reply(f"❌ Lỗi khi gọi API:\n<code>{e}</code>")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
