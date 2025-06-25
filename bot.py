import logging
import requests
import os
import asyncio
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
except:
    pass

# Load biến môi trường
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
AI_API_URL = os.getenv("AI_API_URL", "https://scromnyi-ai.vercel.app/chat")
IMG_API_URL = "https://search-image-dun.vercel.app/search_images"
IMG_API_KEY = "Scromnyi"

# Kiểm tra token
if not BOT_TOKEN:
    raise ValueError("❌ Chưa thiết lập BOT_TOKEN trong .env")

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Xoá tin nhắn sau 10 giây
async def auto_delete(context, chat_id, *message_ids):
    await asyncio.sleep(20)
    for msg_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            logging.warning(f"Không thể xóa tin nhắn {msg_id}: {e}")

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text("🤖 Xin chào! Gửi câu hỏi hoặc dùng /search_images <từ khóa> để tìm ảnh.")
    await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

# Xử lý AI chat
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        url = f"{AI_API_URL}?message={requests.utils.quote(user_message)}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            try:
                ai_reply = response.json().get("response", "").strip()
            except:
                ai_reply = response.text.strip()
        else:
            ai_reply = f"❌ Máy chủ AI lỗi: {response.status_code}"

    except Exception as e:
        logging.warning(f"Lỗi gọi AI API: {e}")
        ai_reply = "⚠️ Không thể kết nối tới máy chủ AI. Vui lòng thử lại sau!"

    reply = f"""
👤 *Bạn:* `{user_message}`
👨‍💻 *AI trả lời:*

{ai_reply}
    """.strip()

    sent = await update.message.reply_text(reply, parse_mode="Markdown")
    await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

# /search_images <query>
async def search_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        sent = await update.message.reply_text("📌 Dùng: /search_images <từ khóa>")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)
        return

    query = " ".join(context.args)
    url = f"{IMG_API_URL}?q={requests.utils.quote(query)}&key={IMG_API_KEY}"
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="upload_photo")

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        images = data.get("images", [])
        valid_images = [img for img in images if img.startswith("https://")]

        if valid_images:
            sent = await update.message.reply_photo(valid_images[0], caption=f"🔍 Kết quả cho: *{query}*", parse_mode="Markdown")
        else:
            sent = await update.message.reply_text("❌ Không có ảnh hợp lệ (chỉ nhận HTTPS).")
    except Exception as e:
        logging.warning(f"Lỗi tìm ảnh: {e}")
        sent = await update.message.reply_text("⚠️ Không thể truy cập dịch vụ ảnh. Vui lòng thử lại sau.")

    await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

# /search_info <query>
async def search_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        sent = await update.message.reply_text("📌 Dùng: /search_info <từ khóa>")
        await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)
        return

    query = " ".join(context.args)
    url = f"{IMG_API_URL}?q={requests.utils.quote(query)}&key={IMG_API_KEY}"
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        images = data.get("images", [])
        valid_images = [img for img in images if img.startswith("https://")]

        if valid_images:
            reply = "\n".join(valid_images[:5])
            sent = await update.message.reply_text(f"🔗 *Kết quả cho:* `{query}`\n{reply}", parse_mode="Markdown")
        else:
            sent = await update.message.reply_text("❌ Không tìm thấy ảnh hợp lệ.")
    except Exception as e:
        logging.warning(f"Lỗi tìm link ảnh: {e}")
        sent = await update.message.reply_text("⚠️ Không thể truy cập dịch vụ ảnh. Vui lòng thử lại sau.")

    await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

# Không phải văn bản
async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sent = await update.message.reply_text("📌 Vui lòng chỉ gửi văn bản!")
    await auto_delete(context, update.effective_chat.id, update.message.message_id, sent.message_id)

# Khởi động bot
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search_images", search_images))
    app.add_handler(CommandHandler("search_info", search_info))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(~filters.TEXT, handle_non_text))

    print("✅ Bot đã khởi động.")
    app.run_polling()
