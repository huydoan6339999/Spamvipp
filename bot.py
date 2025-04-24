import json
import os
import logging
import time
import requests
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler
from keep_alive import keep_alive

# Cấu hình bot
BOT_TOKEN = "6320148381:AAEntoWHszOtVaRTBiPmxYNDyELNqxm-8Ag"
ADMIN_ID = "5736655322"

if not BOT_TOKEN or not ADMIN_ID:
    raise ValueError("LỖI: BOT_TOKEN hoặc ADMIN_ID không được thiết lập!")

DATA_FILE = "treo_data.json"
USER_FILE = "users_data.json"

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load & Save user data
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)

users = load_users()

# Kiểm tra quyền admin
def is_admin(user_id):
    return str(user_id) == str(ADMIN_ID)

# Gửi lỗi cho admin qua Telegram
async def send_error_to_admin(bot, message):
    await bot.send_message(chat_id=ADMIN_ID, text=f"[ERROR] {message}")

# Hàm kiểm tra username TikTok
async def auto_treo(bot):
    for user_id, user_data in users.items():
        username = user_data.get("username", "")
        if not username:
            continue

        url = f"https://apitangfltiktok.soundcast.me/telefl.php?user={username}&userid={user_id}&tokenbot={BOT_TOKEN}"

        try:
            res = requests.get(url, timeout=30)
            if res.status_code == 200:
                result = res.json()
                # Kiểm tra xem API có trả về kết quả hợp lệ không
                if "status" in result and result["status"] == "success":
                    logging.info(f"Auto Treo thành công @{username} - {result.get('message', 'Không có thông tin')}")
                else:
                    logging.warning(f"Auto Treo thất bại @{username}: {result.get('message', 'Không có thông tin')}")
            else:
                logging.error(f"API lỗi khi kiểm tra @{username}: {res.status_code}")
        except requests.exceptions.Timeout:
            logging.warning(f"Timeout khi auto treo @{username}")
        except Exception as e:
            logging.error(f"Lỗi khi auto treo @{username}: {str(e)}")
        await asyncio.sleep(2)  # Giới hạn thời gian giữa các yêu cầu

# Lệnh /fl kiểm tra TikTok và auto treo
async def fl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("Dùng: /fl <username>")

    username = context.args[0].strip().lstrip("@")  # Bỏ @ nếu có
    user_id = update.effective_user.id

    if user_id not in users:
        users[user_id] = {"username": username}
        save_users(users)

    # Kiểm tra tài khoản TikTok
    url = f"https://apitangfltiktok.soundcast.me/telefl.php?user={username}&userid={user_id}&tokenbot={BOT_TOKEN}"
    try:
        res = requests.get(url, timeout=30)
        if res.status_code == 200:
            result = res.json()
            if "status" in result and result["status"] == "success":
                await update.message.reply_text(f"Tài khoản @{username} đã được kiểm tra thành công!")
            else:
                await update.message.reply_text(f"Lỗi khi kiểm tra @{username}: {result.get('message', 'Không có thông tin')}")
        else:
            await update.message.reply_text(f"Lỗi khi kiểm tra @{username}: {res.status_code}")
    except requests.exceptions.Timeout:
        await update.message.reply_text(f"Timeout khi kiểm tra @{username}")
    except Exception as e:
        await update.message.reply_text(f"Lỗi khi kiểm tra @{username}: {str(e)}")

    # Gọi auto treo ngay lập tức và kích hoạt scheduler
    logging.info(f"Đang tự động kiểm tra @{username}...")

    # Gọi hàm auto treo để kiểm tra tất cả người dùng
    await auto_treo(update.bot)

    # Tạo scheduler để tự động treo mỗi 15 phút
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: asyncio.create_task(auto_treo(update.bot)), 'interval', minutes=15)
    scheduler.start()

# Lệnh /adduser
async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Bạn không có quyền thêm người dùng!")

    if not context.args:
        return await update.message.reply_text("Dùng: /adduser <user_id> <username>")

    user_id = context.args[0].strip()
    username = context.args[1].strip().lstrip("@")  # bỏ @ nếu có

    if user_id in users:
        return await update.message.reply_text(f"User {user_id} đã có.")

    users[user_id] = {"username": username}
    save_users(users)
    await update.message.reply_text(f"Đã thêm user {user_id} với username @{username}!")

# Lệnh /listusers
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return await update.message.reply_text("Bạn không có quyền!")

    if not users:
        return await update.message.reply_text("Không có user nào.")

    text = "\n".join([f"{uid}: {data['username']}" for uid, data in users.items()])
    await update.message.reply_text(f"User hiện tại:\n{text}")

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Xin chào! Các lệnh:\n"
        "/adduser <id> <username> - Thêm người dùng\n"
        "/listusers - Danh sách người dùng\n"
        "/fl <username> - Kiểm tra TikTok và tự động treo"
    )

# Main
async def main():
    keep_alive()  # Gọi server giữ bot sống
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adduser", add_user))
    app.add_handler(CommandHandler("listusers", list_users))
    app.add_handler(CommandHandler("fl", fl))  # Thêm handler cho lệnh /fl

    logging.info("Bot đang chạy...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
