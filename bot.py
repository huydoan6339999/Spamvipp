from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import asyncio
import time
from keep_alive import keep_alive  # Nếu bạn có file keep_alive.py thì giữ dòng này

# Token bot và ID user được phép
BOT_TOKEN = "6320148381:AAFDPsDIHpWUfCKWy6kOnpXwm7KztJoZjjs"
ALLOWED_USER_ID = 5736655322

# Biến lưu cooldown và số lần dùng lệnh
cooldowns = {}
usage_count = {}
authorized_users = {ALLOWED_USER_ID}

# Giới hạn số lần dùng lệnh mỗi lần chạy bot
MAX_USAGE = 5

# Hàm /treovip
async def treovip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Kiểm tra quyền
    if user_id not in authorized_users:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng bot này.")
        return

    # Kiểm tra số lần sử dụng
    if user_id in usage_count and usage_count[user_id] >= MAX_USAGE:
        await update.message.reply_text(f"❗ Bạn đã sử dụng lệnh tối đa {MAX_USAGE} lần.")
        return

    current_time = time.time()

    # Kiểm tra cooldown
    if user_id in cooldowns:
        elapsed_time = current_time - cooldowns[user_id]
        if elapsed_time < 30:
            remaining = int(30 - elapsed_time)
            await update.message.reply_text(f"⏳ Vui lòng chờ {remaining} giây trước khi dùng lại.")
            return

    # Kiểm tra có username không
    if not context.args:
        await update.message.reply_text("⚡ Vui lòng nhập username TikTok.\nVí dụ: /treovip baohuydz158")
        return

    username = context.args[0]
    url = f"http://ngocan.infinityfreeapp.com/ntik.php?username={username}&key=ngocanvip"

    # Gửi tin nhắn "đang xử lý"
    processing_message = await update.message.reply_text("⏳ Đang xử lý, vui lòng chờ...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=50) as response:
                if response.status == 200:
                    data = await response.json()

                    if 'followers_add' in data and 'message' in data:
                        await processing_message.edit_text(
                            f"✅ Tự động buff cho `@{username}` thành công!\n"
                            f"➕ Thêm: {data.get('followers_add', 0)}\n"
                            f"💬 {data.get('message', 'Không có')}",
                            parse_mode="Markdown"
                        )
                    else:
                        await processing_message.edit_text("❗ Có lỗi xảy ra, vui lòng thử lại sau.")
                else:
                    await processing_message.edit_text("❗ Có lỗi xảy ra, vui lòng thử lại sau.")
    except Exception:
        await processing_message.edit_text("❗ Có lỗi xảy ra, vui lòng thử lại sau.")

    # Cập nhật cooldown và usage
    cooldowns[user_id] = current_time
    usage_count[user_id] = usage_count.get(user_id, 0) + 1

# Hàm /adduser
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng lệnh này.")
        return

    if not context.args:
        await update.message.reply_text("⚡ Vui lòng nhập user_id cần thêm.")
        return

    try:
        new_user_id = int(context.args[0])
        authorized_users.add(new_user_id)
        await update.message.reply_text(f"✅ Đã thêm user {new_user_id} vào danh sách quyền.")
    except ValueError:
        await update.message.reply_text("❗ User ID không hợp lệ.")
    except Exception as e:
        await update.message.reply_text("❗ Xảy ra lỗi khi thêm user.")

# Khởi tạo app
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Đăng ký lệnh
app.add_handler(CommandHandler("treovip", treovip))
app.add_handler(CommandHandler("adduser", adduser))

# Giữ bot sống (nếu cần)
keep_alive()

# Chạy bot
app.run_polling()
