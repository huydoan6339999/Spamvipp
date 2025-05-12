from pyrogram import Client, filters
import requests
import re
import json

# Cấu hình bot
API_ID = 27657608  # Thay bằng API ID của bạn
API_HASH = "3b6e52a3713b44ad5adaa2bcf579de66"
BOT_TOKEN = "6320148381:AAFUjdFvpOZ2Yw23jfRm4UAjglfSmwgBLbU"

app = Client("like_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Hàm an toàn lấy dữ liệu từ dict
def safe_get(data, key):
    return data.get(key, "Không có")

# Hàm trích số từ chuỗi
def extract_number(value):
    if not value:
        return "Không rõ"
    match = re.search(r'\d+', str(value))
    return match.group() if match else "Không rõ"

# Lệnh /like uid region
@app.on_message(filters.command("like") & filters.private)
async def like_handler(client, message):
    args = message.text.split()

    if len(args) != 3:
        return await message.reply("⚠️ Vui lòng dùng đúng cú pháp: `/like uid region`", quote=True)

    uid = args[1]
    region = args[2].lower()

    # Kiểm tra định dạng đầu vào
    if not uid.isdigit():
        return await message.reply("❌ UID phải là số.", quote=True)
    if region not in ["vn", "id", "th", "sg"]:  # Region hợp lệ
        return await message.reply("❌ Region không hợp lệ. Ví dụ: vn, id, th, sg", quote=True)

    api_url = f"https://scromnyi.onrender.com/like?uid={uid}&region={region}"

    try:
        headers = {"Accept": "application/json"}
        response = requests.get(api_url, timeout=10, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
        except json.JSONDecodeError:
            truncated = response.text[:1000]
            return await message.reply(f"⚠️ Phản hồi không phải JSON hợp lệ:\n\n{truncated}", quote=True)

        # Soạn nội dung phản hồi
        reply_text = (
            "<blockquote>"
            "BUFF LIKE THÀNH CÔNG✅\n"
            f"╭👤 Name: {safe_get(data, 'PlayerNickname')}\n"
            f"├🆔 UID : {safe_get(data, 'uid')}\n"
            f"├🌏 Region : {region}\n"
            f"├📉 Like trước đó: {safe_get(data, 'likes_before')}\n"
            f"├📈 Like sau khi gửi: {safe_get(data, 'likes_after')}\n"
            f"╰👍 Like được gửi: {extract_number(data.get('likes_given'))}"
            "</blockquote>"
        )

        await message.reply(reply_text, quote=True, parse_mode="html")

    except requests.exceptions.Timeout:
        await message.reply("❌ API không phản hồi (timeout). Vui lòng thử lại sau.", quote=True)
    except requests.exceptions.HTTPError as e:
        await message.reply(f"❌ API trả về lỗi HTTP: {e.response.status_code}", quote=True)
    except requests.exceptions.RequestException as e:
        await message.reply(f"⚠️ Lỗi khi kết nối API: {e}", quote=True)

app.run()
