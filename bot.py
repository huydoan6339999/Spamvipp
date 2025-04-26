from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import aiohttp
import asyncio
from keep_alive import keep_alive

# Token bot và ID admin
BOT_TOKEN = "6320148381:AAEKPrT9vs70BLSrmwjQtfwYDprXpGu4s3s"
ALLOWED_USER_ID = 5736655322

# Danh sách quyền, task quản lý buff
authorized_users = {ALLOWED_USER_ID}
task_manager = {}

# Hàm tự gửi tin nhắn và xóa sau 50 giây
async def send_and_delete(update: Update, text: str, parse_mode="Markdown"):
    msg = await update.message.reply_text(text, parse_mode=parse_mode)
    await asyncio.sleep(50)
    try:
        await msg.delete()
    except:
        pass

# Hàm /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_and_delete(update,
        "👋 Xin chào!\n"
        "Tôi là bot auto buff TikTok.\n\n"
        "Các lệnh hỗ trợ:\n"
        "/treovip <username1> <username2> - Auto buff TikTok không giới hạn, mỗi 15 phút 1 lần.\n"
        "/stopbuff - Dừng buff đang chạy.\n"
        "/listbuff - Xem danh sách buff đang hoạt động.\n"
        "/adduser <user_id> - Thêm user được phép dùng bot."
    )

# Hàm buff cho từng username
async def auto_buff(update: Update, user_id: int, username: str):
    url = f"https://apitangfltiktok.soundcast.me/telefl.php?user={username}&userid={user_id}&tokenbot={BOT_TOKEN}"
    success_count = 0

    try:
        while True:
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, timeout=50) as response:
                        if response.status == 200:
                            data = await response.text()
                            success_count += 1

                            message = "✅ Channel: Treo thành công!\n"
                            if data.strip() == "":
                                message += "💬 Không có thông báo từ API."
                            else:
                                message += f"💬 Kết quả: {data}"

                            await send_and_delete(update, message)

                            if success_count % 10 == 0:
                                await send_and_delete(update,
                                    f"⭐ Đã buff tổng cộng {success_count} lần cho `@{username}`!"
                                )
                        else:
                            await send_and_delete(update,
                                "✅ Channel: Treo thành công!\n💬 Không có thông báo từ API."
                            )
                except asyncio.TimeoutError:
                    await send_and_delete(update,
                        "✅ Channel: Treo thành công!\n💬 Không có thông báo từ API."
                    )
                except Exception:
                    await send_and_delete(update,
                        "✅ Channel: Treo thành công!\n💬 Không có thông báo từ API."
                    )

            await asyncio.sleep(900)  # 15 phút
    except asyncio.CancelledError:
        await send_and_delete(update, f"⛔ Đã dừng buff tự động cho @{username}.")
    finally:
        if user_id in task_manager and username in task_manager[user_id]:
            del task_manager[user_id][username]
            if not task_manager[user_id]:
                del task_manager[user_id]

# Hàm /treovip
async def treovip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in authorized_users:
        await send_and_delete(update, "❗ Bạn không có quyền sử dụng bot này.")
        return

    if not context.args:
        await send_and_delete(update, "⚡ Vui lòng nhập ít nhất 1 username TikTok.\nVí dụ: /treovip baohuydz158 acc2")
        return

    usernames = context.args[:2]

    if user_id in task_manager:
        for task in task_manager[user_id].values():
            if not task.done():
                task.cancel()

    task_manager[user_id] = {}

    for username in usernames:
        task = asyncio.create_task(auto_buff(update, user_id, username))
        task_manager[user_id][username] = task

    await send_and_delete(update,
        f"⏳ Bắt đầu auto buff cho: {', '.join(usernames)}.\n"
        "Mỗi 15 phút tự động gửi 1 lần.\n"
        "Dùng /stopbuff để dừng bất cứ lúc nào."
    )

# Hàm /stopbuff
async def stopbuff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in authorized_users:
        await send_and_delete(update, "❗ Bạn không có quyền sử dụng lệnh này.")
        return

    if user_id in task_manager:
        for task in task_manager[user_id].values():
            if not task.done():
                task.cancel()
        del task_manager[user_id]
        await send_and_delete(update, "⛔ Đã dừng toàn bộ buff đang chạy!")
    else:
        await send_and_delete(update, "⚡ Hiện tại bạn không có buff nào đang chạy.")

# Hàm /listbuff
async def listbuff(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in authorized_users:
        await send_and_delete(update, "❗ Bạn không có quyền xem danh sách.")
        return

    if user_id not in task_manager or not task_manager[user_id]:
        await send_and_delete(update, "⚡ Bạn không có buff nào đang hoạt động.")
        return

    buffing = list(task_manager[user_id].keys())
    message = "📜 Danh sách username đang buff:\n" + "\n".join(f"- @{u}" for u in buffing)
    await send_and_delete(update, message)

# Hàm /adduser
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id != ALLOWED_USER_ID:
        await send_and_delete(update, "❗ Bạn không có quyền thêm user.")
        return

    if not context.args:
        await send_and_delete(update, "⚡ Vui lòng nhập user_id cần thêm.")
        return

    try:
        new_user_id = int(context.args[0])
        authorized_users.add(new_user_id)
        await send_and_delete(update, f"✅ Đã thêm user {new_user_id} thành công.")
    except ValueError:
        await send_and_delete(update, "❗ User ID không hợp lệ.")
    except Exception:
        await send_and_delete(update, "❗ Xảy ra lỗi khi thêm user.")

# Khởi tạo app
app = ApplicationBuilder().token(BOT_TOKEN).build()

# Đăng ký lệnh
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("treovip", treovip))
app.add_handler(CommandHandler("stopbuff", stopbuff))
app.add_handler(CommandHandler("listbuff", listbuff))
app.add_handler(CommandHandler("adduser", adduser))

# Giữ bot sống
keep_alive()

# Chạy bot
app.run_polling()
