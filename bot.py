import os
import logging
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= TOKEN =================
TOKEN = os.getenv("BOT_TOKEN")

# 👇 ADD ADMIN CODE HERE (THIS IS THE RIGHT PLACE)
ADMIN_ID = 8869605526

def is_admin(user_id):
    return user_id == ADMIN_ID

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
            "started": False,
            "break": None
        }

    data = user_data[user_id]
    state = data["state"]

    hour = now.hour
    shift_active = (hour >= 19 or hour < 8)

    text = ""

    # ================= START WORK (ONLY SHIFT CHECK) =================
    if q.data == "start":

        if not shift_active:
            await q.message.reply_text("❌ Shift not active (7PM–8AM)")
            return

        data["state"] = "working"
        data["started"] = True

        text = f"🟢 {name} Started Work\n⏰ {now.strftime('%H:%M')}"

    # ================= OFF WORK (ONLY AFTER START) =================
    elif q.data == "off":

        if not data["started"]:
            await q.message.reply_text("❌ You must start work first!")
            return

        data["state"] = "idle"
        data["started"] = False
        data["break"] = None

        text = f"🔴 {name} Ended Work\n⏰ {now.strftime('%H:%M')}"

    # ================= BREAK START =================
    elif q.data in ["smoke", "wash", "prayer", "lunch"]:

        if state != "working":
            await q.message.reply_text("❌ Start work first!")
            return

        if data.get("break"):
            await q.message.reply_text("❌ Finish current break first!")
            return

        data["state"] = "break"
        data["break"] = (q.data, now)

        text = f"🚀 {name} started {q.data} break"

    # ================= BACK TO SEAT =================
    async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    user_id = str(q.from_user.id)
    name = q.from_user.first_name
    now = datetime.now()

    if user_id not in user_data:
        user_data[user_id] = {
            "state": "idle",
            "started": False,
            "break": None
        }

    data = user_data[user_id]
    state = data["state"]

    hour = now.hour
    shift_active = (hour >= 19 or hour < 8)

    text = ""

    # ================= START WORK (ONLY SHIFT CHECK) =================
    if q.data == "start":

        if not shift_active:
            await q.message.reply_text("❌ Shift not active (7PM–8AM)")
            return

        data["state"] = "working"
        data["started"] = True

        text = f"🟢 {name} Started Work\n⏰ {now.strftime('%H:%M')}"

    # ================= OFF WORK (ONLY AFTER START) =================
    elif q.data == "off":

        if not data["started"]:
            await q.message.reply_text("❌ You must start work first!")
            return

        data["state"] = "idle"
        data["started"] = False
        data["break"] = None

        text = f"🔴 {name} Ended Work\n⏰ {now.strftime('%H:%M')}"

    # ================= BREAK START =================
    elif q.data in ["smoke", "wash", "prayer", "lunch"]:

        if state != "working":
            await q.message.reply_text("❌ Start work first!")
            return

        if data.get("break"):
            await q.message.reply_text("❌ Finish current break first!")
            return

        data["state"] = "break"
        data["break"] = (q.data, now)

        text = f"🚀 {name} started {q.data} break"

    # ================= BACK TO SEAT =================
    elif q.data == "back":

        if state != "break":
            await q.message.reply_text("❌ You are not on break!")
            return

        fines = 0
        btype, start = data["break"]

        limits = {
            "smoke": 10,
            "wash": 10,
            "prayer": 15,
            "lunch": 180
        }

        if (now - start).total_seconds() / 60 > limits[btype]:
            fines = 1000

        data["state"] = "working"
        data["break"] = None

        text = f"🔙 {name} Back to Work"

        if fines:
            text += f"\n⚠️ Fine: {fines} PKR"

    # ================= BLOCK INVALID ACTIONS =================
    else:
        if state == "break":
            await q.message.reply_text("❌ Finish break first!")
            return
        if state == "idle" and q.data not in ["start"]:
            await q.message.reply_text("❌ Start work first!")
            return

    if not text:
        text = "⚠️ Action completed"

    await q.message.reply_text(text, reply_markup=menu())

    # ================= BLOCK INVALID ACTIONS =================
    else:
        if state == "break":
            await q.message.reply_text("❌ Finish break first!")
            return
        if state == "idle" and q.data not in ["start"]:
            await q.message.reply_text("❌ Start work first!")
            return

    if not text:
        text = "⚠️ Action completed"

    await q.message.reply_text(text, reply_markup=menu())

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