import logging
import asyncio
import aiohttp
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from keep_alive import keep_alive

# ========== CẤU HÌNH ==========
BOT_TOKEN = "6320148381:AAEzg2-xF4SR0bU4J0rDmdkHAzLTg0CiKZ8"  # <-- Thay bằng token của bạn
ADMINS = [5736655322]               # <-- Thay bằng Telegram ID của bạn
AUTHORIZED_USERS = []              # Những user được phép treo
MAX_TREO = 10                      # Số lượng username có thể treo cùng lúc
API_TIMEOUT = 10                  # Timeout khi gọi API
# ==============================

treo_tasks = {}

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Chào bạn!\n"
        "/treo <username> - Treo TikTok\n"
        "/huytreo <username> - Hủy treo\n"
        "/adduser <user_id> - Thêm người dùng\n"
        "/removeuser <user_id> - Xóa người dùng\n"
        "/list - Danh sách đang treo"
    )

# Treo API mỗi 15p
async def check_loop(username, chat_id, app):
    while True:
        url = f"http://ngocan.infinityfreeapp.com/ntik.php?username={username}&key=ngocanvip"
        try:
            timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    text = await resp.text()
            await app.bot.send_message(chat_id, f"Kết quả `{username}`:\n{text}", parse_mode="Markdown")
        except asyncio.TimeoutError:
            await app.bot.send_message(chat_id, f"⏰ API quá lâu khi kiểm tra `{username}`")
        except Exception as e:
            await app.bot.send_message(chat_id, f"Lỗi: {e}")
        await asyncio.sleep(900)

# /treo
async def treo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMINS and user_id not in AUTHORIZED_USERS:
        return await update.message.reply_text("Bạn không có quyền dùng lệnh này.")
    if len(context.args) == 0:
        return await update.message.reply_text("Nhập username: /treo baohuydz158")
    username = context.args[0]
    if username in treo_tasks:
        return await update.message.reply_text("Username đã được treo.")
    if len(treo_tasks) >= MAX_TREO:
        return await update.message.reply_text("Đạt giới hạn username đang treo.")
    task = asyncio.create_task(check_loop(username, update.effective_chat.id, context.application))
    treo_tasks[username] = task
    await update.message.reply_text(f"Đã bắt đầu treo `{username}`", parse_mode="Markdown")

# /huytreo
async def huytreo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền.")
    if len(context.args) == 0:
        return await update.message.reply_text("Nhập username: /huytreo baohuydz158")
    username = context.args[0]
    task = treo_tasks.get(username)
    if task:
        task.cancel()
        del treo_tasks[username]
        await update.message.reply_text(f"Đã hủy treo `{username}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("Username không được treo.")

# /adduser
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền.")
    if len(context.args) == 0:
        return await update.message.reply_text("Nhập user ID: /adduser 123456")
    try:
        uid = int(context.args[0])
        if uid in AUTHORIZED_USERS:
            return await update.message.reply_text("User đã có quyền.")
        AUTHORIZED_USERS.append(uid)
        await update.message.reply_text(f"Đã thêm user ID {uid}")
    except:
        await update.message.reply_text("Sai định dạng user ID.")

# /removeuser
async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền.")
    if len(context.args) == 0:
        return await update.message.reply_text("Nhập user ID: /removeuser 123456")
    try:
        uid = int(context.args[0])
        if uid not in AUTHORIZED_USERS:
            return await update.message.reply_text("User không có trong danh sách.")
        AUTHORIZED_USERS.remove(uid)
        await update.message.reply_text(f"Đã xóa user ID {uid}")
    except:
        await update.message.reply_text("Sai định dạng user ID.")

# /list
async def list_treo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền.")
    if not treo_tasks:
        return await update.message.reply_text("Không có username nào đang treo.")
    danh_sach = "\n".join(f"- {u}" for u in treo_tasks.keys())
    await update.message.reply_text(f"Đang treo:\n{danh_sach}")

# Khởi chạy bot
async def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("treo", treo))
    app.add_handler(CommandHandler("huytreo", huytreo))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("removeuser", removeuser))
    app.add_handler(CommandHandler("list", list_treo))

    print("Bot đang chạy...")
    await app.run_polling()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
