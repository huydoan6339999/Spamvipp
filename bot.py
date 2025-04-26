from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import asyncio
import time
from keep_alive import keep_alive  # Nếu bạn có file keep_alive.py thì giữ lại

# Token bot và ID admin
BOT_TOKEN = "TOKEN_CUA_BAN"
ALLOWED_USER_ID = 5736655322

# Danh sách quyền, cooldown, số lần dùng lệnh
authorized_users = {ALLOWED_USER_ID}
cooldowns = {}
usage_count = {}

# Quản lý task buff của từng user
task_manager = {}

# Hàm /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xin chào!\n"
        "Tôi là bot auto buff TikTok.\n\n"
        "Các lệnh hỗ trợ:\n"
        "/treovip <username> - Auto buff 15 phút/lần, không giới hạn.\n"
        "/stopbuff - Dừng buff đang chạy.\n"
        "/adduser <user_id> - Thêm user được phép dùng bot."
    )

# Hàm /treovip
async def treovip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in authorized_users:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng bot này.")
        return

    if not context.args:
        await update.message.reply_text("⚡ Vui lòng nhập username TikTok.\nVí dụ: /treovip baohuydz158")
        return

    username = context.args[0]
    url = f"http://ngocan.infinityfreeapp.com/ntik.php?username={username}&key=ngocanvip"

    await update.message.reply_text(
        f"⏳ Bắt đầu auto buff cho `@{username}`.\n"
        f"Mỗi lần cách nhau 15 phút.\n"
        f"Dùng /stopbuff để dừng bất kỳ lúc nào.",
        parse_mode="Markdown"
    )

    # Nếu đã có task cũ, hủy trước
    if user_id in task_manager:
        task_manager[user_id].cancel()

    # Hàm chạy auto buff
    async def auto_buff():
        try:
            count = 1
            while True:
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(url, timeout=50) as response:
                            if response.status == 200:
                                data = await response.json()

                                if 'followers_add' in data and 'message' in data:
                                    await update.message.reply_text(
                                        f"✅ Buff lần {count} cho `@{username}` thành công!\n"
                                        f"➕ Thêm: {data.get('followers_add', 0)}\n"
                                        f"💬 {data.get('message', 'Không có')}",
                                        parse_mode="Markdown"
                                    )
                                else:
                                    await update.message.reply_text(f"❗ Lỗi dữ liệu lần {count}.")
                            else:
                                await update.message.reply_text(f"❗ Lỗi kết nối lần {count}.")
                    except Exception:
                        await update.message.reply_text(f"❗ Lỗi mạng lần {count}.")

                count += 1
                await asyncio.sleep(900)  # 15 phút
        except asyncio.CancelledError:
            await update.message.reply_text("⛔ Đã dừng auto buff theo yêu cầu.")
        finally:
            if user_id in task_manager:
                del task_manager[user_id]

    # Khởi động task buff
    task = asyncio.create_task(auto_buff())
    task_manager[user_id] = task

# Hàm /stopbuff
async def stopbuff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in authorized_users:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng lệnh này.")
        return

    task = task_manager.get(user_id)

    if task:
        task.cancel()
        await update.message.reply_text("⛔ Đã dừng buff!")
    else:
        await update.message.reply_text("⚡ Bạn không có buff nào đang chạy.")

# Hàm /adduser
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("❗ Bạn không có quyền thêm user.")
        return

    if not context.args:
        await update.message.reply_text("⚡ Vui lòng nhập user_id cần thêm.")
        return

    try:
        new_user_id = int(context.args[0])
        authorized_users.add(new_user_id)
        await update.message.reply_text(f"✅ Đã thêm user {new_user_id} thành công.")
    except ValueError:
        await update.message.reply_text("❗ User ID không hợp lệ.")
    except Exception:
        await update.message.reply_text("❗ Xảy ra lỗi khi thêm user.")

# Khởi tạo app
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Đăng ký lệnh
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("treovip", treovip))
app.add_handler(CommandHandler("stopbuff", stopbuff))
app.add_handler(CommandHandler("adduser", adduser))

# Giữ bot sống
keep_alive()

# Chạy bot
app.run_polling()
