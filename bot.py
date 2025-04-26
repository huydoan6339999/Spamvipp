from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import asyncio
import time
from keep_alive import keep_alive

# Token bot và ID admin
BOT_TOKEN = "6320148381:AAHsYxu-9Go8UAvNYtPE2hRLmPSbimRE8F8"
ALLOWED_USER_ID = 5736655322

# Danh sách quyền, task quản lý buff
authorized_users = {ALLOWED_USER_ID}
task_manager = {}

# Hàm /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Xin chào!\n"
        "Tôi là bot auto buff TikTok.\n\n"
        "Các lệnh hỗ trợ:\n"
        "/treovip <username1> <username2> - Auto buff TikTok không giới hạn, mỗi 15 phút 1 lần.\n"
        "/stopbuff - Dừng buff đang chạy.\n"
        "/adduser <user_id> - Thêm user được phép dùng bot."
    )

# Hàm buff cho từng username
async def auto_buff(update: Update, user_id: int, username: str):
    url = f"https://apitangfltiktok.soundcast.me/telefl.php?user={username}&userid={user_id}&tokenbot={BOT_TOKEN}"
    success_count = 0  # Đếm số lần thành công

    try:
        while True:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, timeout=50) as response:
                        if response.status == 200:
                            data = await response.text()
                            success_count += 1
                            await update.message.reply_text(
                                f"✅ Buff lần {success_count} cho `@{username}`!\n"
                                f"💬 Kết quả: {data}",
                                parse_mode="Markdown"
                            )

                            if success_count % 10 == 0:
                                await update.message.reply_text(
                                    f"⭐ Đã buff tổng cộng {success_count} lần cho `@{username}`!",
                                    parse_mode="Markdown"
                                )
                        else:
                            await update.message.reply_text(f"❗ Lỗi kết nối khi buff `@{username}`.")
                except Exception:
                    await update.message.reply_text(f"❗ Lỗi mạng khi buff `@{username}`.")

            await asyncio.sleep(900)  # 15 phút
    except asyncio.CancelledError:
        await update.message.reply_text(f"⛔ Đã dừng buff tự động cho @{username}.")
    finally:
        if user_id in task_manager and username in task_manager[user_id]:
            del task_manager[user_id][username]
            if not task_manager[user_id]:  # Nếu không còn task nào
                del task_manager[user_id]

# Hàm /treovip
async def treovip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in authorized_users:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng bot này.")
        return

    if not context.args:
        await update.message.reply_text("⚡ Vui lòng nhập ít nhất 1 username TikTok.\nVí dụ: /treovip baohuydz158 acc2")
        return

    usernames = context.args[:2]  # Lấy tối đa 2 username

    # Nếu đang buff cũ, dừng lại
    if user_id in task_manager:
        for task in task_manager[user_id].values():
            task.cancel()

    task_manager[user_id] = {}

    for username in usernames:
        task = asyncio.create_task(auto_buff(update, user_id, username))
        task_manager[user_id][username] = task

    await update.message.reply_text(
        f"⏳ Bắt đầu auto buff cho: {', '.join(usernames)}.\n"
        "Mỗi 15 phút tự động gửi 1 lần.\n"
        "Dùng /stopbuff để dừng bất cứ lúc nào.",
        parse_mode="Markdown"
    )

# Hàm /stopbuff
async def stopbuff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in authorized_users:
        await update.message.reply_text("❗ Bạn không có quyền sử dụng lệnh này.")
        return

    if user_id in task_manager:
        for task in task_manager[user_id].values():
            task.cancel()
        del task_manager[user_id]
        await update.message.reply_text("⛔ Đã dừng toàn bộ buff đang chạy!")
    else:
        await update.message.reply_text("⚡ Hiện tại bạn không có buff nào đang chạy.")

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
