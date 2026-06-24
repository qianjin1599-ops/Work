import logging
import os
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= CONFIG =================
logging.basicConfig(level=logging.INFO)

# Use environment variable (SAFE)
TOKEN = "8968085641:AAGkQ2pfG5fa-Tz9LiqOLRGctE0jW3lso-M"

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set. Please set it in environment variables.")

# store user sessions
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
        "👨‍💼 Attendance Bot Started\nSelect your action:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BUTTON HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    now = datetime.now()

    if user_id not in user_data:
        user_data[user_id] = {}

    data = user_data[user_id]
    text = "⚠️ Action recorded"

    # -------- START WORK --------
    if query.data == "start_work":
        data["start_time"] = now
        text = "🟢 Work Started (Shift 7PM - 8AM)"

    # -------- OFF WORK --------
    elif query.data == "off":
        data["end_time"] = now
        text = "🔴 Work Ended"

    # -------- LUNCH --------
    elif query.data == "lunch":
        data["lunch_limit"] = now + timedelta(hours=3)
        text = "🍔 Lunch Started (3 hours limit)"

    # -------- WASHROOM --------
    elif query.data == "washroom":
        data["wash_limit"] = now + timedelta(minutes=10)
        text = "🚽 Washroom Started (10 min limit)"

    # -------- SMOKE --------
    elif query.data == "smoke":
        data["smoke_limit"] = now + timedelta(minutes=10)
        text = "☕️ Smoke Break Started (10 min limit)"

    # -------- PRAYER --------
    elif query.data == "prayer":
        data["prayer_limit"] = now + timedelta(minutes=15)
        text = "🙏 Prayer Started (15 min limit)"

    # -------- BACK TO SEAT + FINES --------
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

        text = "💺 Back to Seat"

        if fines > 0:
            text += f"\n⚠️ Fine Applied: {fines} PKR"

    # rebuild keyboard every time
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

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("🤖 Bot is running...")
    app.run_polling()

if name == "main":
    main()
