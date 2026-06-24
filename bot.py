import os
import sqlite3
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

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
    user TEXT,
    action TEXT,
    start_time TEXT,
    end_time TEXT,
    duration TEXT,
    fine INTEGER,
    date TEXT
)
""")
conn.commit()

# ================= MEMORY =================
user_data = {}

SHIFT_START = 19  # 7 PM
SHIFT_END = 8      # 8 AM next day

# ================= MENU =================
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("🚬 Smoke Break", callback_data="smoke")],
        [InlineKeyboardButton("🚻 Washroom Break", callback_data="wash")],
        [InlineKeyboardButton("🕌 Prayer Break", callback_data="prayer")],
        [InlineKeyboardButton("🍽 Lunch Break", callback_data="lunch")],
        [InlineKeyboardButton("🔙 Back to Seat", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")],
        [InlineKeyboardButton("📊 Report", callback_data="report")]
    ])

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💼 Attendance Bot Active",
        reply_markup=menu()
    )

# ================= HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user = q.from_user.first_name
    user_id = q.from_user.id
    now = datetime.now()

    if user_id not in user_data:
        user_data[user_id] = {"active": None}

    data = user_data[user_id]

    text = ""

    # ================= SHIFT CHECK =================
    hour = now.hour
    allowed = (hour >= SHIFT_START or hour < SHIFT_END)

    # ================= START =================
    if q.data == "start":
        if not allowed:
            text = "❌ Shift not active (7PM - 8AM only)"
        else:
            data["start"] = now
            data["active"] = "work"
            text = f"🟢 {user} Started Work\n⏰ {now.strftime('%H:%M')}"

    # ================= BREAKS =================
    elif q.data == "smoke":
        data["break"] = ("smoke", now)
        text = "🚬 Smoke Break Started (10 min)"

    elif q.data == "wash":
        data["break"] = ("wash", now)
        text = "🚻 Washroom Break Started (10 min)"

    elif q.data == "prayer":
        data["break"] = ("prayer", now)
        text = "🕌 Prayer Break Started (15 min)"

    elif q.data == "lunch":
        data["break"] = ("lunch", now)
        text = "🍽 Lunch Break Started (3 hours)"

    # ================= BACK =================
    elif q.data == "back":
        fines = 0

        if "break" in data:
            btype, start = data["break"]
            diff = now - start

            limits = {
                "smoke": 10,
                "wash": 10,
                "prayer": 15,
                "lunch": 180
            }

            limit = limits.get(btype, 0)

            if diff.total_seconds() / 60 > limit:
                fines += 1000

            data.pop("break")

        text = f"🔙 {user} Back to Seat"

        if fines > 0:
            text += f"\n⚠️ Fine Applied: {fines} PKR"

    # ================= OFF =================
    elif q.data == "off":
        data["end"] = now
        data["active"] = None
        text = f"🔴 {user} Ended Work\n⏰ {now.strftime('%H:%M')}"
        # ================= REPORT =================
    elif q.data == "report":
        cursor.execute("SELECT * FROM logs WHERE user=?", (user,))
        rows = cursor.fetchall()
        text = f"📊 Report for {user}\nTotal Records: {len(rows)}"

    # ================= SEND =================
    await q.message.reply_text(text, reply_markup=menu())

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()