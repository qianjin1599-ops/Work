import os
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= TOKEN =================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set!")

# ================= ADMIN =================
ADMIN_ID = 8869605526  # CHANGE THIS

def is_admin(uid):
    return uid == ADMIN_ID

# ================= MEMORY =================
user_data = {}

# ================= SHIFT CONFIG =================
SHIFT_START_HOUR = 19  # 7 PM
SHIFT_END_HOUR = 8      # 8 AM

# ================= MENU =================
def menu(user_id):
    buttons = [
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("🚬 Smoke", callback_data="smoke")],
        [InlineKeyboardButton("🚻 Washroom", callback_data="wash")],
        [InlineKeyboardButton("🕌 Prayer", callback_data="prayer")],
        [InlineKeyboardButton("🍽 Lunch", callback_data="lunch")],
        [InlineKeyboardButton("🔙 Back", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")],
    ]

    if is_admin(user_id):
        buttons.append([InlineKeyboardButton("📊 Report", callback_data="report")])

    return InlineKeyboardMarkup(buttons)

# ================= SHIFT CHECK =================
def is_shift_time():
    hour = datetime.now().hour
    return hour >= SHIFT_START_HOUR or hour < SHIFT_END_HOUR

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💼 HR Attendance Bot Active",
        reply_markup=menu(update.effective_user.id)
    )

# ================= GET CHAT ID =================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"📌 Chat ID:\n{chat_id}")

# ================= BUTTON HANDLER =================
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    uid = str(q.from_user.id)
    name = q.from_user.first_name
    now = datetime.now()

    if uid not in user_data:
        user_data[uid] = {
            "state": "idle",
            "break": None,
            "start_time": None,
            "late_fine": 0
        }

    data = user_data[uid]
    state = data["state"]

    text = ""

    # ================= START WORK =================
    if q.data == "start":

        if not is_shift_time():
            await q.bot.send_message(
    chat_id=q.message.chat_id,
    text=text,
    reply_markup=menu(int(uid))
)"❌ Shift allowed only 7PM - 8AM")
            return

        # 🚨 LATE DETECTION
        if now.hour > SHIFT_START_HOUR or (now.hour == SHIFT_START_HOUR and now.minute > 0):
            data["late_fine"] = 1000
        else:
            data["late_fine"] = 0

        data["state"] = "working"
        data["start_time"] = now

        text = f"🟢 {name} started work"

        if data["late_fine"]:
            text += f"\n⚠️ Late Fine: ₹1000"

    # ================= OFF WORK =================
    elif q.data == "off":
        data["state"] = "idle"
        data["break"] = None
        text = f"🔴 {name} ended work"

    # ================= BREAK START =================
    elif q.data in ["smoke", "wash", "prayer", "lunch"]:

        if state != "working":
            await q.message.reply_text("❌ Start work first!")
            return

        if data["break"]:
            await q.message.reply_text("❌ Already on break!")
            return

        data["break"] = (q.data, now)
        data["state"] = "break"

        text = f"🚀 {name} started {q.data} break"

    # ================= BACK =================
    elif q.data == "back":

        if state != "break":
            await q.message.reply_text("❌ Not on break!")
            limits = {
            "smoke": 10,
            "wash": 10,
            "prayer": 15,
            "lunch": 180
        }

        btype, start_time = data["break"]
        minutes = (now - start_time).total_seconds() / 60

        fine = 0

        if minutes > limits[btype]:
            fine = 500

        data["break"] = None
        data["state"] = "working"

        text = f"🔙 {name} back to work"

        if fine:
            text += f"\n⚠️ Break Fine: ₹500"

    # ================= REPORT =================
    elif q.data == "report":

        if not is_admin(int(uid)):
            await q.message.reply_text("❌ Admin only")
            return

        text = "📊 HR REPORT\n\n"

        for u, d in user_data.items():
            text += f"{u}: {d}\n"

   await q.bot.send_message(
    chat_id=q.message.chat_id,
    text=text,
    reply_markup=menu(int(uid))
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