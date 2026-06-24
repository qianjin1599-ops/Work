import logging
import os
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= TOKEN (RAILWAY SAFE) =================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set!")

# ================= MEMORY STORE =================
user_data = {}

# ================= START COMMAND =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟢 Start Work", callback_data="start_work")],
        [InlineKeyboardButton("🍔 Lunch Break", callback_data="lunch")],
        [InlineKeyboardButton("🚽 Washroom", callback_data="washroom")],
        [InlineKeyboardButton("☕️ Smoke", callback_data="smoke")],
        [InlineKeyboardButton("🙏 Prayer", callback_data="prayer")],
        [InlineKeyboardButton("💺 Back to Seat", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")]
    ]

    await update.message.reply_text(
        "👨‍💼 Attendance Bot Active\nSelect your action:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BUTTON HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    name = query.from_user.first_name
    now = datetime.now()

    if user_id not in user_data:
        user_data[user_id] = {}

    data = user_data[user_id]
    text = ""

    # ================= ACTIONS =================
    if query.data == "start_work":
        data["start"] = now
        text = f"🟢 {name} Started Work\n⏰ {now.strftime('%H:%M')}"

    elif query.data == "lunch":
        data["lunch_limit"] = now + timedelta(hours=3)
        text = f"🍔 {name} Lunch Started (3 hours limit)"

    elif query.data == "washroom":
        data["wash_limit"] = now + timedelta(minutes=10)
        text = f"🚽 {name} Washroom Started (10 min limit)"

    elif query.data == "smoke":
        data["smoke_limit"] = now + timedelta(minutes=10)
        text = f"☕️ {name} Smoke Break Started (10 min limit)"

    elif query.data == "prayer":
        data["prayer_limit"] = now + timedelta(minutes=15)
        text = f"🙏 {name} Prayer Started (15 min limit)"

    elif query.data == "off":
        data["end"] = now
        text = f"🔴 {name} Ended Work\n⏰ {now.strftime('%H:%M')}"

    elif query.data == "back":
        fines = 0

        if "wash_limit" in data and now > data["wash_limit"]:
            fines += 1000
        if "smoke_limit" in data and now > data["smoke_limit"]:
            fines += 1000
        if "prayer_limit" in data and now > data["prayer_limit"]:
            fines += 1000
        if "lunch_limit" in data and now > data["lunch_limit"]:
            fines += 1000

        text = f"💺 {name} Back to Seat"

        if fines > 0:
            text += f"\n⚠️ Fine Applied: {fines} PKR"

    # ================= KEYBOARD =================
    keyboard = [
        [InlineKeyboardButton("🟢 Start Work", callback_data="start_work")],
        [InlineKeyboardButton("🍔 Lunch Break", callback_data="lunch")],
        [InlineKeyboardButton("🚽 Washroom", callback_data="washroom")],
        [InlineKeyboardButton("☕️ Smoke", callback_data="smoke")],
        [InlineKeyboardButton("🙏 Prayer", callback_data="prayer")],
        [InlineKeyboardButton("💺 Back to Seat", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")]
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= MAIN FUNCTION =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
print("Bot is running...")
    app.run_polling()

# ================= ENTRY POINT =================
if name == "main":
    main()