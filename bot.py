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
    raise ValueError("BOT_TOKEN is not set!")

# ================= MEMORY =================
user_data = {}

# ================= MENU =================
def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("🚬 Smoke Break", callback_data="smoke")],
        [InlineKeyboardButton("🚻 Washroom", callback_data="wash")],
        [InlineKeyboardButton("🕌 Prayer Break", callback_data="prayer")],
        [InlineKeyboardButton("🍽 Lunch Break", callback_data="lunch")],
        [InlineKeyboardButton("🔙 Back to Seat", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💼 Attendance Bot Ready",
        reply_markup=get_menu()
    )

# ================= BUTTON HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user.first_name
    user_id = query.from_user.id
    now = datetime.now()

    if user_id not in user_data:
        user_data[user_id] = {}

    data = user_data[user_id]

    text = "⚠️ Action recorded"

    try:

        # ================= START =================
        if query.data == "start":
            data["start"] = now
            text = f"🟢 {user} Started Work\n⏰ {now.strftime('%H:%M')}"

        # ================= BREAKS =================
        elif query.data == "smoke":
            data["smoke"] = now
            data["smoke_limit"] = now + timedelta(minutes=10)
            text = f"🚬 {user} Smoke Break Started"

        elif query.data == "wash":
            data["wash"] = now
            data["wash_limit"] = now + timedelta(minutes=10)
            text = f"🚻 {user} Washroom Started"

        elif query.data == "prayer":
            data["prayer"] = now
            data["prayer_limit"] = now + timedelta(minutes=15)
            text = f"🕌 {user} Prayer Started"

        elif query.data == "lunch":
            data["lunch"] = now
            data["lunch_limit"] = now + timedelta(hours=3)
            text = f"🍽 {user} Lunch Started"

        # ================= BACK =================
        elif query.data == "back":
            fines = 0

            if "smoke_limit" in data and now > data["smoke_limit"]:
                fines += 1000
            if "wash_limit" in data and now > data["wash_limit"]:
                fines += 1000
            if "prayer_limit" in data and now > data["prayer_limit"]:
                fines += 1000
            if "lunch_limit" in data and now > data["lunch_limit"]:
                fines += 1000

            text = f"🔙 {user} Back to Seat"

            if fines > 0:
                text += f"\n⚠️ Fine: {fines} PKR"

        # ================= OFF =================
        elif query.data == "off":
            text = f"🔴 {user} Ended Work\n⏰ {now.strftime('%H:%M')}"

        # ================= MENU =================
        elif query.data == "menu":
            text = "👨‍💼 Main Menu"

        # ================= SAFETY =================
        if not text or text.strip() == "":
            text = "⚠️ Action completed"

        await query.message.reply_text(text, reply_markup=get_menu())

    except Exception as e:
        await query.message.reply_text(f"❌ Error: {str(e)}", reply_markup=get_menu())
# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    # FIX FOR RAILWAY + CONFLICT ERROR
    app.bot.delete_webhook(drop_pending_updates=True)

    print("Bot is running...")
    app.run_polling()

if name == "main":
    main()