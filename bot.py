import logging
import requests
import os
import asyncio
import json
from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, ContextTypes,
    CommandHandler, MessageHandler, filters
)
from dotenv import load_dotenv

# Optional nếu dùng Replit hoặc cần giữ bot online
try:
    from keep_alive import keep_alive
    keep_alive()
except Exception as e:
    logging.warning(f"Lỗi keep_alive: {e}")

# Load biến môi trường
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_API_URL = os.getenv("AI_API_URL", "https://scromnyi-ai.vercel.app/chat")
LIKE_API_URL = "https://likes-scromnyi.vercel.app/like"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Giới hạn yêu cầu mỗi ngày
MAX_REQUESTS_PER_DAY = 60

def load_request_data():
    try:
        with open("requests.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_request_data(data):
    with open("requests.json", "w") as f:
        json.dump(data, f, indent=4)

def check_daily_limit(user_id):
    data = load_request_data()
    today = datetime.now().strftime("%Y-%m-%d")

    if str(user_id) not in data:
        data[str(user_id)] = {"date": today, "requests": 0}
        save_request_data(data)

    user_data = data[str(user_id)]

    if user_data["date"] != today:
        user_data["date"] = today
        user_data["requests"] = 0
        save_request_data(data)

    if user_data["requests"] >= MAX_REQUESTS_PER_DAY:
        return False
    return True

def increment_user_request(user_id):
    data = load_request_data()
    user_data = data[str(user_id)]
    user_data["requests"] += 1
    save_request_data(data)

# Xoá tin nhắn sau 10 giây
async def auto_delete(context, chat_id, *message_ids):
    await asyncio.sleep(10)
    for msg_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            logging.warning(f"Không thể xóa tin nhắn {msg_id}: {e}")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sent = await update.message.reply_text("🤖 Xin chào! Gửi câu hỏi hoặc dùng /like <uid> <region> để tăng lượt thích.")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)
    except Exception as e:
        logging.error(f"Lỗi /start: {e}")

# Xử lý AI chat
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not check_daily_limit(user_id):
        sent = await update.message.reply_text("❌ Bạn đã đạt giới hạn 60 yêu cầu trong ngày.")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)
        return

    try:
        user_message = update.message.text
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

        url = f"{AI_API_URL}?message={requests.utils.quote(user_message)}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            try:
                ai_reply = response.json().get("response", "").strip()
            except Exception:
                ai_reply = response.text.strip()
        else:
            ai_reply = f"❌ Máy chủ AI lỗi: {response.status_code}"

        reply = f"""
👤 *Bạn:* `{user_message}`
👨‍💻 *AI trả lời:*

{ai_reply}
        """.strip()

        sent = await update.message.reply_text(reply, parse_mode="Markdown")
        increment_user_request(user_id)
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

    except Exception as e:
        logging.error(f"Lỗi xử lý AI: {e}")
        sent = await update.message.reply_text("⚠️ Đã xảy ra lỗi. Vui lòng thử lại sau.")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

# Lệnh /like
async def like(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not check_daily_limit(user_id):
        sent = await update.message.reply_text("❌ Bạn đã đạt giới hạn 60 yêu cầu trong ngày.")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)
        return

    if len(context.args) < 2:
        sent = await update.message.reply_text("📌 Cú pháp: /like <uid> <region>")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)
        return

    try:
        uid = context.args[0]
        region = context.args[1]
        url = f"{LIKE_API_URL}?uid={uid}&region={region}"

        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                sent = await update.message.reply_text(f"✅ Đã tăng lượt thích cho UID `{uid}` ở khu vực `{region}`.")
                increment_user_request(user_id)
            else:
                sent = await update.message.reply_text(f"❌ Lỗi: {data.get('message', 'Không xác định')}")
        else:
            sent = await update.message.reply_text(f"❌ Lỗi API: {response.status_code}")

        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

    except Exception as e:
        logging.error(f"Lỗi /like: {e}")
        sent = await update.message.reply_text("⚠️ Đã xảy ra lỗi khi gọi API. Vui lòng thử lại sau.")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

# Xử lý tin nhắn không hỗ trợ
async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sent = await update.message.reply_text("📌 Vui lòng chỉ gửi văn bản hoặc lệnh hợp lệ!")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)
    except Exception as e:
        logging.error(f"Lỗi xử lý tin nhắn không hỗ trợ: {e}")

# Khởi động bot
if __name__ == '__main__':
    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("like", like))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        app.add_handler(MessageHandler(~filters.TEXT, handle_non_text))

        print("✅ Bot đã khởi động.")
        app.run_polling()

    except Exception as e:
        logging.error(f"Lỗi khởi động bot: {e}")
