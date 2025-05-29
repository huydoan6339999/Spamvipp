from pyrogram import Client, filters
import requests
import re
import json
from keep_alive import keep_alive  # Import keep_alive.py

# Cấu hình bot
BOT_TOKEN = "6320148381:AAHFlcIoGCj7iST1P3jGL7W4ZAaAdM1tsU0"

app = Client("like_bot", bot_token=BOT_TOKEN)

# Kích hoạt keep_alive trước khi chạy bot
keep_alive()

# Các hàm và logic bot
def safe_get(data, key):
    return data.get(key, "Không có")

def extract_number(value):
    try:
        return str(int(value))
    except (ValueError, TypeError):
        match = re.search(r'[\d,.]+', str(value))
        return match.group() if match else "Không rõ"

@app.on_message(filters.command("like") & filters.private)
async def like_handler(client, message):
    args = message.text.split()

    if len(args) != 3:
        return await message.reply("⚠️ Vui lòng dùng đúng cú pháp: `/like uid region`", quote=True)

    uid = args[1]
    region = args[2].lower()

    if not uid.isdigit():
        return await message.reply("❌ UID phải là số.", quote=True)
    if region not in ["vn", "id", "th", "sg"]:
        return await message.reply("❌ Region không hợp lệ. Ví dụ: vn, id, th, sg", quote=True)

    api_url = f"https://likes-application.vercel.app/like?uid={uid}&region={region}"

    try:
        headers = {"Accept": "application/json"}
        response = requests.get(api_url, timeout=10, headers=headers)
        response.raise_for_status()

        try:
            data = response.json()
        except json.JSONDecodeError:
            truncated = response.text[:1000]
            return await message.reply(f"⚠️ Phản hồi không phải JSON hợp lệ:\n\n{truncated}", quote=True)

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
