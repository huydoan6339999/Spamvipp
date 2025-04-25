import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio
import aiohttp
from keep_alive import keep_alive  # Import keep_alive

# ========== CẤU HÌNH ==========
BOT_TOKEN = "6320148381:AAEntoWHszOtVaRTBiPmxYNDyELNqxm-8Ag"  # <-- Thay bằng bot token của bạn
ADMINS = [5736655322]               # <-- Thay bằng Telegram user ID của admin
AUTHORIZED_USERS = []              # Danh sách người dùng được phép treo (chỉ admin có thể thêm vào)
MAX_TREO = 10                      # Giới hạn tối đa username được treo cùng lúc
API_TIMEOUT = 30                   # Thời gian timeout API (10 giây)
# ==============================

treo_tasks = {}

# Hàm gọi API mỗi 15 phút với timeout
async def check_loop(username, chat_id, app: Application):
    while True:
        url = f"http://ngocan.infinityfreeapp.com/ntik.php?username={username}&key=ngocanvip"
        
        try:
            # Cấu hình timeout cho API
            timeout = aiohttp.ClientTimeout(total=API_TIMEOUT)
            
            # Gửi yêu cầu API với timeout
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    text = await resp.text()
            
            # Gửi kết quả cho người dùng
            await app.bot.send_message(chat_id=chat_id, text=f"Kết quả cho `{username}`:\n{text}", parse_mode="Markdown")
        except asyncio.TimeoutError:
            await app.bot.send_message(chat_id=chat_id, text=f"⏰ Lỗi: API mất quá nhiều thời gian để phản hồi khi kiểm tra `{username}`.")
        except Exception as e:
            await app.bot.send_message(chat_id=chat_id, text=f"Lỗi khi kiểm tra `{username}`:\n{e}")
        
        # Chờ 15 phút (900 giây) trước khi kiểm tra lại
        await asyncio.sleep(900)  # 15 phút

# Lệnh /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    welcome_message = (
        f"Chào {user_name}, chào mừng bạn đến với Bot TikTok.\n"
        "Bot này giúp bạn kiểm tra tài khoản TikTok mỗi 15 phút.\n\n"
        "Các lệnh có sẵn:\n"
        "/treo <username> - Bắt đầu treo tài khoản TikTok\n"
        "/huytreo <username> - Hủy treo tài khoản TikTok\n"
        "/adduser <user_id> - Thêm người dùng vào danh sách được phép treo (Admin)\n"
        "/removeuser <user_id> - Xóa người dùng khỏi danh sách (Admin)\n"
        "/list - Xem danh sách các tài khoản đang treo\n"
        "/start - Hiển thị thông tin hướng dẫn sử dụng bot"
    )
    await update.message.reply_text(welcome_message)

# Lệnh /treo
async def treo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS and update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền dùng lệnh này.")

    if len(context.args) == 0:
        return await update.message.reply_text("Vui lòng nhập username TikTok.\nVí dụ: /treo baohuydz158")

    if len(treo_tasks) >= MAX_TREO:
        return await update.message.reply_text(f"Đã đạt giới hạn {MAX_TREO} username đang treo. Hãy hủy treo một username trước.")

    username = context.args[0]
    if username in treo_tasks:
        return await update.message.reply_text("Username này đã được treo.")

    task = asyncio.create_task(check_loop(username, update.effective_chat.id, context.application))
    treo_tasks[username] = task
    await update.message.reply_text(f"✅ Đã bắt đầu treo `{username}` mỗi 15 phút.", parse_mode="Markdown")

# Lệnh /huytreo
async def huytreo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền dùng lệnh này.")

    if len(context.args) == 0:
        return await update.message.reply_text("Vui lòng nhập username để hủy treo.\nVí dụ: /huytreo baohuydz158")

    username = context.args[0]
    task = treo_tasks.get(username)
    if task:
        task.cancel()
        del treo_tasks[username]
        await update.message.reply_text(f"❌ Đã hủy treo `{username}`.", parse_mode="Markdown")
    else:
        await update.message.reply_text("Username này không nằm trong danh sách đang treo.")

# Lệnh /adduser
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền dùng lệnh này.")

    if len(context.args) == 0:
        return await update.message.reply_text("Vui lòng nhập Telegram ID của user cần thêm.\nVí dụ: /adduser 987654321")

    user_id = int(context.args[0])

    if user_id in AUTHORIZED_USERS:
        return await update.message.reply_text(f"User ID {user_id} đã có quyền treo rồi.")

    AUTHORIZED_USERS.append(user_id)
    await update.message.reply_text(f"✅ Đã thêm user ID {user_id} vào danh sách được phép treo.")

# Lệnh /removeuser
async def removeuser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền dùng lệnh này.")

    if len(context.args) == 0:
        return await update.message.reply_text("Vui lòng nhập Telegram ID của user cần xóa.\nVí dụ: /removeuser 987654321")

    user_id = int(context.args[0])

    if user_id not in AUTHORIZED_USERS:
        return await update.message.reply_text(f"User ID {user_id} không có quyền treo.")

    AUTHORIZED_USERS.remove(user_id)
    await update.message.reply_text(f"✅ Đã xóa user ID {user_id} khỏi danh sách được phép treo.")

# Lệnh /list
async def list_treo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text("Bạn không có quyền dùng lệnh này.")

    if not treo_tasks:
        return await update.message.reply_text("Không có username nào đang được treo.")
    
    danh_sach = '\n'.join(f"- `{u}`" for u in treo_tasks.keys())
    await update.message.reply_text(f"Username đang treo:\n{danh_sach}", parse_mode="Markdown")

# Khởi động bot và server Flask
async def main():
    keep_alive()  # Giữ bot luôn hoạt động

    app = Application.builder().token(BOT_TOKEN).build()

    # Thêm các handler cho các lệnh bot
    app.add_handler(CommandHandler("start", start))  # Thêm handler cho lệnh /start
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
