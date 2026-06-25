import os
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# ================= LOGGING =================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# ================= TOKEN =================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing in environment variables")

# ================= MEMORY =================
user_data = {}

# ================= SHIFT =================
SHIFT_START = 19
SHIFT_END = 8

# ================= MENU =================
def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("🚬 Smoke Break", callback_data="smoke")],
        [InlineKeyboardButton("🚻 Washroom", callback_data="washroom")],
        [InlineKeyboardButton("🕌 Prayer Break", callback_data="prayer")],
        [InlineKeyboardButton("🍽 Lunch Break", callback_data="lunch")],
        [InlineKeyboardButton("🔙 Back to Seat", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")]
    ])

# ================= SHIFT CHECK =================
def is_shift_active():
    hour = datetime.now().hour
    return hour >= SHIFT_START or hour < SHIFT_END

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💼 Attendance Bot Started",
        reply_markup=get_menu()
    )

# ================= CALLBACK =================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    name = query.from_user.first_name
    now = datetime.now()

    if user_id not in user_data:
        user_data[user_id] = {
            "state": "idle",
            "break": None,
            "start": None,
            "fine": 0
        }

    data = user_data[user_id]
    state = data["state"]
    text = ""

    # ================= START WORK =================
    if query.data == "start":
        if not is_shift_active():
            text = "❌ Shift time is 7PM - 8AM only"
        else:
            data["state"] = "working"
            data["start"] = now
            text = f"🟢 {name} started work"

    # ================= OFF =================
    elif query.data == "off":
        data["state"] = "idle"
        data["break"] = None
        text = f"🔴 {name} ended work"

    # ================= BREAK =================
    elif query.data in ["smoke", "washroom", "prayer", "lunch"]:

        if state != "working":
            text = "❌ Start work first"
        elif data["break"]:
            text = "❌ Already on break"
        else:
            data["break"] = (query.data, now)
            data["state"] = "break"
            text = f"🚀 {name} started {query.data} break"

    # ================= BACK =================
    elif query.data == "back":

        if state != "break":
            text = "❌ Not on break"
        else:
            limits = {
                "smoke": 10,
                "washroom": 10,
                "prayer": 15,
                "lunch": 180
            }

            break_type, start_time = data["break"]
            minutes = (now - start_time).total_seconds() / 60

            fine = 0
            if minutes > limits[break_type]:
                fine = 1000

            data["break"] = None
            data["state"] = "working"

            text = f"🔙 Back to seat"

            if fine:
                text += f"\n⚠️ Fine: ₹{fine}"

    # ================= SEND =================
    await query.message.reply_text(
        text,
        reply_markup=get_menu()
    )

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("Bot is running...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()