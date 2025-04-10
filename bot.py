import telebot
import os
import tempfile
import subprocess
from keep_alive import keep_alive

# Token của bot (đã thay thế với token của bạn)
TOKEN = "6320148381:AAEmECeVkZqhyqVgzuGiKM96907l41MxkC4"
bot = telebot.TeleBot(TOKEN)

name_bot = "Bảo Huy"

# Xử lý lệnh /spam
@bot.message_handler(commands=['spam'])
def spam(message):
    params = message.text.split()[1:]  # Tách thông tin từ tin nhắn lệnh
    if len(params) != 2:
        # Nếu số tham số không đúng, gửi lại hướng dẫn sử dụng
        bot.reply_to(message, "Dùng như này nhé: /spam sdt số_lần")
        return

    sdt, count = params

    # Kiểm tra xem số lần spam có phải là một số hợp lệ không
    if not count.isdigit():
        bot.reply_to(message, "Vui lòng nhập số lần hợp lệ.")
        return

    count = int(count)  # Chuyển số lần spam sang kiểu int

    # Gửi thông báo cho người dùng
    bot.send_message(message.chat.id, f'''
┌──────⭓ {name_bot}
│ Spam: Thành Công 
│ Số Lần Spam Free: {count}
│ Đang Tấn Công : {sdt}
└─────────────
    ''')

    try:
        # Kiểm tra xem file "dec.py" có tồn tại không
        if not os.path.isfile("dec.py"):
            bot.reply_to(message, "Không tìm thấy file script dec.py.")
            return

        # Đọc nội dung script từ file dec.py
        with open("dec.py", 'r', encoding='utf-8') as f:
            script = f.read()

        # Tạo file tạm thời và ghi nội dung script vào đó
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as tmp:
            tmp.write(script.encode('utf-8'))
            temp_path = tmp.name

        # Chạy script bằng subprocess
        subprocess.Popen(["python", temp_path, sdt, str(count)])
    except Exception as e:
        # Nếu có lỗi xảy ra, thông báo lỗi cho người dùng
        bot.reply_to(message, f"Lỗi: {str(e)}")

# Kích hoạt web server keep_alive (nếu có)
keep_alive()

# Chạy bot
print("Bot đang chạy...")
bot.polling()
