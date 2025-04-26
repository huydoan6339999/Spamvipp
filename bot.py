import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import time
from keep_alive import keep_alive

# Tải các biến môi trường từ tệp .env
load_dotenv()

# Lấy API key và BOT token từ biến môi trường
API_KEY = os.getenv("API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ALLOWED_USER_ID = 5736655322  # Thay bằng user_id của bạn

cooldowns = {}
usage_count = {}
authorized_users = {ALLOWED_USER_ID}  # Khởi tạo với người dùng của bạn là người duy nhất có quyền

MAX_USAGE = 5

async def treovip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in authorized_users:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng bot này.")
        return

    if user_id in usage_count and usage_count[user_id] >= MAX_USAGE:
        await update.message.reply_text(f"❗ Bạn đã sử dụng lệnh tối đa {MAX_USAGE} lần.")
        return

    current_time = time.time()

    if user_id in cooldowns:
        elapsed_time = current_time - cooldowns[user_id]
        if elapsed_time < 30:
            remaining = int(30 - elapsed_time)
            await update.message.reply_text(f"⏳ Vui lòng chờ {remaining} giây trước khi dùng lệnh lại.")
            return

    if not context.args:
        await update.message.reply_text("⚡ Vui lòng nhập username TikTok.\nVí dụ: /treovip baohuydz158")
        return

    username = context.args[0]
    url = f"http://ngocan.infinityfreeapp.com/ntik.php?username={username}&key={API_KEY}"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(
                f"✅ Tự động buff cho `@{username}` thành công!\n"
                f"➕ Thêm: {data.get('followers_add', 0)}\n"
                f"💬 {data.get('message', 'Không có')}",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(f"❗ Lỗi API: {response.status_code}")
    except Exception as e:
        await update.message.reply_text(f"❗ Lỗi kết nối API:\n`{str(e)}`", parse_mode="Markdown")

    cooldowns[user_id] = current_time
    if user_id not in usage_count:
        usage_count[user_id] = 0
    usage_count[user_id] += 1

async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("⚡ Vui lòng nhập user_id của người dùng cần thêm vào danh sách.")
        return

    try:
        new_user_id = int(context.args[0])  # Lấy user_id từ tham số
        authorized_users.add(new_user_id)
        await update.message.reply_text(f"✅ Người dùng {new_user_id} đã được thêm vào danh sách quyền.")
    except ValueError:
        await update.message.reply_text("❗ User ID không hợp lệ. Vui lòng nhập một số nguyên.")
    except Exception as e:
        await update.message.reply_text(f"❗ Lỗi xảy ra khi thêm người dùng:\n{str(e)}")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("treovip", treovip))
app.add_handler(CommandHandler("adduser", adduser))

keep_alive()

app.run_polling()
