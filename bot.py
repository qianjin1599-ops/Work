import os
import sqlite3
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

# ================= DATABASE =================
conn = sqlite3.connect("attendance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT,
    name TEXT,
    action TEXT,
    start_time TEXT,
    end_time TEXT,
    fine INTEGER,
    date TEXT
)
""")
conn.commit()

# ================= MEMORY =================
user_data = {}

SHIFT_START = 19   # 7 PM
SHIFT_END = 8      # 8 AM

# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("🚬 Smoke", callback_data="smoke")],
        [InlineKeyboardButton("🚻 Washroom", callback_data="wash")],
        [InlineKeyboardButton("🕌 Prayer", callback_data="prayer")],
        [InlineKeyboardButton("🍽 Lunch", callback_data="lunch")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
        [InlineKeyboardButton("🔴 Off", callback_data="off")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💼 Attendance Bot Active",
        reply_markup=menu()
    )

# ================= BUTTON HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = str(q.from_user.id)
    name = q.from_user.first_name
    now = datetime.now()

    if user_id not in user_data:
        user_data[user_id] = {
            "state": "idle",
            "break": None
        }

    data = user_data[user_id]
    state = data["state"]

    hour = now.hour
    shift_active = (hour >= SHIFT_START or hour < SHIFT_END)

    text = "⚠️ Action recorded"

    # ================= SHIFT CHECK =================
    if q.data == "start" and not shift_active:
        await q.message.reply_text("❌ Shift not active (7PM–8AM)")
        return

    # ================= START WORK =================
    if q.data == "start":
        data["state"] = "working"
        text = f"🟢 {name} Started Work\n⏰ {now.strftime('%H:%M')}"

    # ================= BREAK START =================
    elif q.data in ["smoke", "wash", "prayer", "lunch"]:
        if state != "working":
            await q.message.reply_text("❌ Start work first!")
            return

        data["state"] = "break"
        data["break"] = (q.data, now)

        text = f"🚀 {name} started {q.data} break"

    # ================= BACK =================
    elif q.data == "back":
        fines = 0

        if data.get("break"):
            btype, start = data["break"]

            limits = {
                "smoke": 10,
                "wash": 10,
                "prayer": 15,
                "lunch": 180
            }

            limit = limits[btype]

            if (now - start).total_seconds() / 60 > limit:
                fines += 1000

            data["break"] = None

        data["state"] = "working"

        text = f"🔙 {name} Back to Seat"

        if fines:
            text += f"\n⚠️ Fine Applied: {fines} PKR"

    # ================= OFF =================
    elif q.data == "off":
        data["state"] = "idle"
        data["break"] = None
        text = f"🔴 {name} Ended Work\n⏰ {now.strftime('%H:%M')}"
        # ================= INVALID ACTION LOCK =================
    else:
        if state == "break":
            await q.message.reply_text("❌ You must finish break first!")
            return
        if state == "idle":
            await q.message.reply_text("❌ You must start work first!")
            return

    # ================= SAFE SEND =================
    if not text:
        text = "⚠️ Done"

    await q.message.reply_text(text, reply_markup=menu())

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    # FIX: avoid webhook conflict on Railway
    app.bot.delete_webhook(drop_pending_updates=True)

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()