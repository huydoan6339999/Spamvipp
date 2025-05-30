import logging
import time
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from keep_alive import keep_alive

# === CẤU HÌNH BOT ===
BOT_TOKEN = "6320148381:AAH_ihVyyOGOHOfDU-XFhi0an-tKXdtgL50"

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# === GIỮ BOT HOẠT ĐỘNG (CHO REPLIT/GLITCH) ===
keep_alive()

# === HÀM HỖ TRỢ ===
def safe_get(data, key, default="N/A"):
    value = data.get(key)
    return str(value) if value is not None else default

def extract_number(text):
    if not text:
        return "0"
    return ''.join(c for c in str(text) if c.isdigit())

# === LỆNH START ===
@dp.message_handler(commands=["start", "help"])
async def start_handler(message: types.Message):
    await message.reply(
        "👋 Xin chào!\n"
        "Gửi lệnh:\n<code>/like uid region</code>\n"
        "Ví dụ: <code>/like 123456789 SEA</code>"
    )

# === LỆNH /LIKE ===
@dp.message_handler(commands=["like"])
async def like_handler(message: types.Message):
    args = message.text.strip().split()

    if len(args) != 3:
        await message.reply("❌ Sai cú pháp!\nDùng: <code>/like uid region</code>\nVí dụ: <code>/like 123456789 SEA</code>")
        return

    uid = args[1]
    region = args[2]
    api_url = f"https://likes-application.vercel.app/like?uid={uid}&region={region}"
    start_time = time.time()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                elapsed = time.time() - start_time
                try:
                    data = await resp.json()
                except Exception:
                    text_data = await resp.text()
                    await message.reply(
                        f"❌ API trả về không đúng định dạng JSON.\n"
                        f"<code>{text_data}</code>\n"
                        f"⏱ Phản hồi sau {elapsed:.2f} giây"
                    )
                    return

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
                    reply_text = (
                        "❌ API trả về lỗi.\n"
                        f"<code>{data}</code>\n"
                        f"⏱ Phản hồi sau {elapsed:.2f} giây"
                    )

                await message.reply(reply_text)

    except Exception as e:
        await message.reply(f"❌ Lỗi khi gọi API:\n<code>{str(e)}</code>")

# === CHẠY BOT ===
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    executor.start_polling(dp, skip_updates=True)
