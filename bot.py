from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging, random
from keep_alive import keep_alive

BOT_TOKEN = "6320148381:AAH-_OKdwtZNKky9NXEx0zoWezcuEIoSEo8"

rules_dict = {
    3: "Xỉu", 4: "68% Xỉu", 5: "Xỉu", 6: "Nghỉ",
    7: {"exact": ["124", "223", "133"], "result": "Xỉu", "default": "Tài"},
    8: {"exact": ["134"], "result": "Xỉu", "default": "Tài"},
    9: {"exact": ["234"], "result": "Xỉu", "default": "Tài (50/50)"},
    10: "Xỉu (auto)", 11: "Nghỉ",
    12: {"exact": ["246", "156", "336", "255"], "result": "Xỉu", "default": "Tài"},
    13: {"exact": ["553", "661", "531", "631"], "result": "Xỉu", "default": "Tài"},
    14: "50/50", 15: "Tài", 16: "Xỉu", 17: "Cẩn thận", 18: "Tài"
}

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎲 Bot SunWin Dự Đoán Tài Xỉu\n"
        "👉 /login <username> <password>\n"
        "👉 /predict <phiên1> <phiên2>..."
    )

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Dùng: /login <username> <password>")
        return
    username, password = context.args
    if username == "baohuy1109" and password == "036320":
        await update.message.reply_text("✅ Đăng nhập thành công!")
    else:
        await update.message.reply_text("❌ Sai tài khoản!")

async def predict(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        session_numbers = [int(num) for num in context.args]
    except:
        await update.message.reply_text("⚠️ Sai cú pháp. Ví dụ: /predict 3 4 5")
        return
    result = predict_outcome(session_numbers)
    await update.message.reply_text(f"🔮 Dự đoán: {result}")

def predict_outcome(session_numbers):
    last = session_numbers[-1]
    rule = rules_dict.get(last)
    if isinstance(rule, str):
        if "Xỉu" in rule:
            return "Xỉu ✅"
        elif "Tài" in rule:
            return "Tài ✅"
        elif "50/50" in rule:
            return random.choice(["Tài", "Xỉu"])
        else:
            return "⚠️ Nên nghỉ tay"
    elif isinstance(rule, dict):
        seq = "".join(str(x) for x in session_numbers[-3:])
        return rule["result"] if seq in rule["exact"] else rule["default"]
    return random.choice(["Tài", "Xỉu"]) + " (random)"

def main():
    keep_alive()
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("login", login))
    app.add_handler(CommandHandler("predict", predict))
    print("🤖 Bot đã sẵn sàng!")
    app.run_polling()

if __name__ == "__main__":
    main()
