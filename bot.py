from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import time
from keep_alive import keep_alive  # Thêm dòng này để gọi keep_alive.py

# Thay token bot của bạn ở đây
BOT_TOKEN = "6320148381:AAFDPsDIHpWUfCKWy6kOnpXwm7KztJoZjjs"

# ID người dùng của bạn (sử dụng /start để lấy user_id)
ALLOWED_USER_ID = 5736655322  # Thay bằng user_id của bạn

# Dictionary lưu thời gian, số lần sử dụng lệnh và danh sách người dùng có quyền
cooldowns = {}
usage_count = {}
authorized_users = {ALLOWED_USER_ID}  # Khởi tạo với người dùng của bạn là người duy nhất có quyền

# Giới hạn số lần sử dụng lệnh
MAX_USAGE = 5

# Hàm xử lý lệnh /treovip
async def treovip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Kiểm tra xem người dùng có được phép sử dụng bot không
    if user_id not in authorized_users:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng bot này.")
        return

    # Kiểm tra số lần đã sử dụng lệnh
    if user_id in usage_count and usage_count[user_id] >= MAX_USAGE:
        await update.message.reply_text(f"❗ Bạn đã sử dụng lệnh tối đa {MAX_USAGE} lần.")
        return

    current_time = time.time()

    # Kiểm tra cooldown
    if user_id in cooldowns:
        elapsed_time = current_time - cooldowns[user_id]
        if elapsed_time < 30:
            remaining = int(30 - elapsed_time)
            await update.message.reply_text(f"⏳ Vui lòng chờ {remaining} giây trước khi dùng lệnh lại.")
            return

    # Kiểm tra tham số username
    if not context.args:
        await update.message.reply_text(
            "⚡ Vui lòng nhập username TikTok.\nVí dụ: /treovip baohuydz158"
        )
        return

    username = context.args[0]
    url = f"http://ngocan.infinityfreeapp.com/ntik.php?username={username}&key=ngocanvip"

    try:
        response = requests.get(url, timeout=100)
        if response.status_code == 200:
            # Parse JSON data
            data = response.json()

            # Gửi thông báo thành công với dữ liệu chi tiết mà không hiển thị thông tin về API
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

    # Cập nhật thời gian và số lần sử dụng lệnh
    cooldowns[user_id] = current_time
    if user_id not in usage_count:
        usage_count[user_id] = 0
    usage_count[user_id] += 1

# Hàm xử lý lệnh /adduser
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Kiểm tra xem người dùng có quyền thêm người dùng không (chỉ admin của bot có quyền này)
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng lệnh này.")
        return

    # Kiểm tra tham số username
    if not context.args:
        await update.message.reply_text("⚡ Vui lòng nhập user_id của người dùng cần thêm vào danh sách.")
        return

    try:
        new_user_id = int(context.args[0])  # Lấy user_id từ tham số
        authorized_users.add(new_user_id)  # Thêm người dùng vào danh sách quyền
        await update.message.reply_text(f"✅ Người dùng {new_user_id} đã được thêm vào danh sách quyền.")
    except ValueError:
        await update.message.reply_text("❗ User ID không hợp lệ. Vui lòng nhập một số nguyên.")
    except Exception as e:
        await update.message.reply_text(f"❗ Lỗi xảy ra khi thêm người dùng:\n{str(e)}")

# Khởi tạo app
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Đăng ký các lệnh
app.add_handler(CommandHandler("treovip", treovip))
app.add_handler(CommandHandler("adduser", adduser))

# Chạy keep_alive để giữ bot luôn hoạt động
keep_alive()  # Gọi keep_alive để duy trì kết nối

# Chạy bot
app.run_polling()
