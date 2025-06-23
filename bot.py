import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from keep_alive import keep_alive

# 🔑 Thay bằng token bot thật của bạn
BOT_TOKEN = "6320148381:AAH-_OKdwtZNKky9NXEx0zoWezcuEIoSEo8"

# 🧾 Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 💬 Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Xin chào! Gửi mình bất kỳ câu hỏi nào và mình sẽ trả lời qua AI!")

# 📥 Xử lý tin nhắn văn bản
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user = update.effective_user.first_name or "người dùng"

    # Gửi trạng thái "đang gõ..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        url = f"https://scromnyi-ai.vercel.app/chat?message={requests.utils.quote(user_message)}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            result = response.text.strip()
        else:
            result = f"❌ API lỗi: {response.status_code}"

    except Exception as e:
        result = f"⚠️ Lỗi khi gọi API: {e}"

    await update.message.reply_text(result)

# 🚫 Xử lý ảnh/sticker/khác
async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Vui lòng chỉ gửi tin nhắn văn bản!")

# 🚀 Khởi động bot
if __name__ == '__main__':
    keep_alive()  # Khởi động web server để giữ bot sống

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(~filters.TEXT, handle_non_text))

    print("🤖 Bot đã khởi động. Sẵn sàng phục vụ!")
    app.run_polling()
