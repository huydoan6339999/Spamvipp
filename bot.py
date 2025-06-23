import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from keep_alive import keep_alive

# 🔐 Token trực tiếp (đã thay)
BOT_TOKEN = "6320148381:AAH-_OKdwtZNKky9NXEx0zoWezcuEIoSEo8"

# 🚨 Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# 🎉 Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Hãy gửi mình bất kỳ câu hỏi nào, mình sẽ trả lời qua AI.")

# 💬 Xử lý văn bản
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    user_name = update.effective_user.first_name or "bạn"

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    try:
        url = f"https://scromnyi-ai.vercel.app/chat?message={requests.utils.quote(user_message)}"
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            try:
                ai_reply = response.json().get("response", "").strip()
            except:
                ai_reply = response.text.strip()
        else:
            ai_reply = f"❌ API lỗi: {response.status_code}"

    except Exception as e:
        ai_reply = f"⚠️ Lỗi khi gọi API:\n`{e}`"

    reply = f"""
👤 *Bạn:* `{user_message}`
🤖 *AI trả lời:*

{ai_reply}
    """.strip()

    await update.message.reply_text(reply, parse_mode="Markdown")

# 🚫 Không phải văn bản
async def handle_non_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 Vui lòng chỉ gửi văn bản để mình có thể trả lời!")

# 🚀 Khởi động bot
if __name__ == '__main__':
    keep_alive()

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(~filters.TEXT, handle_non_text))

    print("✅ Bot đã khởi động.")
    app.run_polling()
