import logging
import json
import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from sunwin_login import login_to_sunwin
from sunwin_predictor import predict_outcome
from pattern_detector import detect_pattern
from keep_alive import keep_alive

BOT_TOKEN = "6320148381:AAH-_OKdwtZNKky9NXEx0zoWezcuEIoSEo8"  # <-- thay bằng token bot

logging.basicConfig(level=logging.INFO)

history = []  # Lưu lịch sử Tài/Xỉu

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎲 SunWin Bot\n"
        "/login <user> <pass> – đăng nhập\n"
        "/predict <3 4 5> – dự đoán\n"
        "/addresult <T/X> – lưu lịch sử\n"
        "/pattern – xem cầu hiện tại"
    )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Dùng: /login <user> <pass>")
        return
    user, pwd = context.args
    result = login_to_sunwin(user, pwd)
    if result.get("success"):
        await update.message.reply_text("✅ Đăng nhập thành công!\nToken: " + result["token"][:30] + "...")
    else:
        await update.message.reply_text("❌ Đăng nhập thất bại!\n" + result.get("message", ""))

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Gõ: /predict <3 4 5>")
        return
    try:
        numbers = list(map(int, context.args))
        msg = predict_outcome(numbers)
        await update.message.reply_text(f"🔮 Phiên {numbers[-1]} → {msg}")
    except:
        await update.message.reply_text("⚠️ Nhập sai định dạng.")

async def add_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history
    if not context.args or context.args[0].upper() not in ["T", "X"]:
        await update.message.reply_text("Gõ: /addresult <T hoặc X>")
        return
    result = context.args[0].upper()
    history.append(result)
    await update.message.reply_text(f"✅ Đã thêm kết quả: {result}. Tổng: {len(history)}")

async def pattern(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = detect_pattern(history)
    if result:
        await update.message.reply_text(f"📊 Phát hiện: {result['description']}\n💡 Gợi ý: {result['advice']}")
    else:
        await update.message.reply_text("🤖 Không nhận diện được cầu nào từ lịch sử.")

def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("predict", predict))
    app.add_handler(CommandHandler("addresult", add_result))
    app.add_handler(CommandHandler("pattern", pattern))
    app.run_polling()

if __name__ == "__main__":
    main()
