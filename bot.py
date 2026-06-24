import os
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= TOKEN =================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN not set")

# ================= DATA =================
user_data = {}

# ================= SHIFT =================
def in_shift():
    now = datetime.now()
    return now.hour >= 19 or now.hour < 8

# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("🚬 Smoke", callback_data="smoke")],
        [InlineKeyboardButton("🚻 Washroom", callback_data="wash")],
        [InlineKeyboardButton("🕌 Prayer", callback_data="prayer")],
        [InlineKeyboardButton("🍽 Lunch", callback_data="lunch")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👨‍💼 Attendance Bot Ready", reply_markup=menu())

# ================= CHAT ID =================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID: {update.effective_chat.id}")

# ================= BUTTON HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query

    # ⚠️ MUST BE FIRST LINE ALWAYS
    await q.answer()

    uid = str(q.from_user.id)
    name = q.from_user.first_name
    now = datetime.now()

    if uid not in user_data:
        user_data[uid] = {
            "state": "idle",
            "break": None,
            "start": None,
            "late": False
        }

    data = user_data[uid]
    state = data["state"]

    text = ""

    # ================= START WORK =================
    if q.data == "start":

        if not in_shift():
            text = "❌ Shift is 7PM - 8AM only"
        else:
            data["start"] = now
            data["state"] = "working"

            data["late"] = now.hour > 19

            text = f"🟢 {name} started work"

            if data["late"]:
                text += "\n⚠️ Late Fine: ₹1000"

    # ================= OFF =================
    elif q.data == "off":
        data["state"] = "idle"
        data["break"] = None
        text = f"🔴 {name} ended work"

    # ================= BREAK START =================
    elif q.data in ["smoke", "wash", "prayer", "lunch"]:

        if state != "working":
            text = "❌ Start work first"
        elif data["break"]:
            text = "❌ Already on break"
        else:
            data["break"] = (q.data, now)
            data["state"] = "break"
            text = f"🚀 {name} started {q.data}"

    # ================= BACK =================
    elif q.data == "back":

        if state != "break":
            text = "❌ Not on break"
        else:
            limits = {
                "smoke": 10,
                "wash": 10,
                "prayer": 15,
                "lunch": 180
            }

            btype, start = data["break"]
            mins = (now - start).total_seconds() / 60

            fine = 0
            if mins > limits[btype]:
                fine = 500

            data["break"] = None
            data["state"] = "working"

            text = f"🔙 {name} back to work"

            if fine:
                text += "\n⚠️ Fine: ₹500"

    # ================= SEND MESSAGE SAFELY =================
    await q.bot.send_message(
        chat_id=q.message.chat_id,
        text=text,
        reply_markup=menu()
    )

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot running...")
    app.run_polling()

# ================= RUN =================
if __name__ == "__main__":
    main()