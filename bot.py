from keep_alive import keep_alive
import telebot
import requests
import time
import threading
from functools import wraps

# Giữ bot online
keep_alive()

# Token bot Telegram
TOKEN = "6374595640:AAHZm45pZN6QFx2UAdj4CcfA1KZ2ZC09Y7c"
bot = telebot.TeleBot(TOKEN)

# ID nhóm và ID admin
GROUP_ID = -1002221629819
ADMIN_ID = 5736655322  # Thay bằng Telegram user_id của bạn

# Cooldown và số lần sử dụng dictionary
user_cooldowns = {}
user_usage_count = {}  # Đếm số lần thực hiện lệnh
MAX_USAGE_COUNT = 10  # Giới hạn 10 lần

# Hàm kiểm tra cooldown
def is_on_cooldown(user_id, command):
    now = time.time()
    key = f"{user_id}_{command}"
    if key in user_cooldowns:
        if now - user_cooldowns[key] < 30:  # Cooldown 30 giây
            return True
    user_cooldowns[key] = now
    return False

# Hàm kiểm tra giới hạn số lần sử dụng lệnh
def check_usage_limit(user_id, command):
    if user_id not in user_usage_count:
        user_usage_count[user_id] = 0
    if user_usage_count[user_id] >= MAX_USAGE_COUNT:
        return False  # Đã vượt quá số lần sử dụng
    user_usage_count[user_id] += 1
    return True

# Reset số lần sử dụng sau 1 giờ
def reset_usage_count():
    while True:
        time.sleep(3600)  # Chờ 1 giờ
        user_usage_count.clear()  # Đặt lại số lần sử dụng của tất cả người dùng

# Decorator chỉ dùng trong nhóm
def only_in_group(func):
    @wraps(func)
    def wrapper(message):
        if message.chat.id != GROUP_ID:
            bot.reply_to(message, "❌ Lệnh này chỉ sử dụng được trong nhóm @Baohuydevs được chỉ định.")
            return
        return func(message)
    return wrapper

# Hàm kiểm tra cooldown, số lần sử dụng và thực thi lệnh
def execute_with_checks(message, command, action):
    user_id = message.from_user.id
    if is_on_cooldown(user_id, command):
        bot.reply_to(message, "❌ Bạn đang trong thời gian chờ, vui lòng thử lại sau 30 giây.")
        return
    if not check_usage_limit(user_id, command):
        bot.reply_to(message, f"❌ Bạn đã sử dụng lệnh này {MAX_USAGE_COUNT} lần trong 1 giờ. Vui lòng thử lại sau.")
        return
    action(message)

# Tự động gọi API mỗi 15 phút
def auto_buff(username, chat_id, user_id):
    if user_id not in auto_buff_tasks:
        return  # Đã bị huỷ

    api_url = f"https://http://ngocan.infinityfreeapp.com/ntik.php?username={username}&key=ngocanvip"
    try:
        response = requests.get(api_url, timeout=80)
        data = response.json()
        bot.send_message(chat_id, f"✅ Tự động buff cho `@{username}` thành công!\n"
                                  f"➕ Thêm: {data.get('followers_add', 0)}\n"
                                  f"💬 {data.get('message', 'Không có')}",
                         parse_mode="Markdown")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Lỗi khi tự động buff: {e}")

    if user_id in auto_buff_tasks:
        task = threading.Timer(900, auto_buff, args=[username, chat_id, user_id])  # Thực hiện lại sau 15 phút
        auto_buff_tasks[user_id] = task
        task.start()

# Lệnh /buff bắt đầu quá trình tự động buff
@bot.message_handler(commands=['buff'])
@only_in_group
def handle_buff(message):
    execute_with_checks(message, "buff", lambda msg: bot.reply_to(msg, "Tự động buff đang chạy..."))

# Lệnh /start để khởi tạo cho người dùng khi tham gia nhóm
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Chào mừng bạn đến với bot của chúng tôi! Hãy sử dụng các lệnh đã được thiết lập.")

# Lệnh /help để hướng dẫn người dùng
@bot.message_handler(commands=['help'])
def handle_help(message):
    bot.reply_to(message, "Các lệnh có sẵn:\n"
                           "/buff - Thực hiện buff tự động cho tài khoản.\n"
                           "/start - Khởi tạo bot.\n"
                           "/help - Hiển thị hướng dẫn.")

# Thực thi lệnh /treo2 (ví dụ lệnh kiểm tra thông tin tài khoản TikTok)
@bot.message_handler(commands=['treo2'])
@only_in_group
def handle_treo2(message):
    execute_with_checks(message, "treo2", lambda msg: bot.reply_to(msg, "Đang kiểm tra tài khoản TikTok..."))

# Đảm bảo bot tiếp tục chạy
keep_alive()

# Bắt đầu một thread để reset số lần sử dụng sau mỗi giờ
threading.Thread(target=reset_usage_count, daemon=True).start()
