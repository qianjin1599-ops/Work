import os
import logging
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from apscheduler.schedulers.asyncio import AsyncIOScheduler

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

# ================= TOKEN =================
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN is not set!")

# ================= ADMIN =================
ADMIN_ID = 1234567890  # 🔥 CHANGE THIS

def is_admin(user_id):
    return user_id == ADMIN_ID

# ================= GROUP =================
GROUP_ID = -1001234567890  # 🔥 CHANGE THIS

# ================= MEMORY =================
user_data = {}

# ================= MENU =================
def menu(user_id):
    buttons = [
        [InlineKeyboardButton("🟢 Start Work", callback_data="start")],
        [InlineKeyboardButton("🚬 Smoke Break", callback_data="smoke")],
        [InlineKeyboardButton("🚻 Washroom Break", callback_data="wash")],
        [InlineKeyboardButton("🕌 Prayer Break", callback_data="prayer")],
        [InlineKeyboardButton("🍽 Lunch Break", callback_data="lunch")],
        [InlineKeyboardButton("🔙 Back to Seat", callback_data="back")],
        [InlineKeyboardButton("🔴 Off Work", callback_data="off")],
    ]

    if is_admin(user_id):
        buttons.append([InlineKeyboardButton("📊 Admin Report", callback_data="report")])

    return InlineKeyboardMarkup(buttons)

# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👨‍💼 Attendance Bot Active",
        reply_markup=menu(update.effective_user.id),
    )

# ================= DAILY REPORT =================
async def send_daily_report(app):
    text = "📊 DAILY REPORT\n\n"

    if not user_data:
        text += "No activity today."
    else:
        for uid, data in user_data.items():
            text += f"User {uid}: {data}\n"

    await app.bot.send_message(chat_id=GROUP_ID, text=text)

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

    shift_active = now.hour >= 19 or now.hour < 8

    text = ""

    # ================= START =================
    if q.data == "start":
        if not shift_active:
            await q.message.reply_text("❌ Shift is 7PM - 8AM only")
            return

        data["state"] = "working"
        data["started"] = True
        text = f"🟢 {name} started work"

    # ================= OFF =================
    elif q.data == "off":
        if not data["started"]:
            await q.message.reply_text("❌ Start work first!")
            return

        data["state"] = "idle"
        data["started"] = False
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

        data["state"] = "break"
        data["break"] = (q.data, now)
        text = f"🚀 {name} started {q.data} break"

    # ================= BACK =================
    elif q.data == "back":
        if state != "break":
            await q.message.reply_text("❌ Not on break!")
            return

        limits = {
            "smoke": 10,
            "wash": 10,
            "prayer": 15,
            "lunch": btype, start_time = data["break"]
        minutes = (now - start_time).total_seconds() / 60

        fine = 0
        if minutes > limits[btype]:
            fine = 500

        data["state"] = "working"
        data["break"] = None

        text = f"🔙 {name} back to work"

        if fine:
            text += f"\n⚠️ Fine: {fine} PKR"

    # ================= ADMIN REPORT =================
    elif q.data == "report":
        if not is_admin(int(user_id)):
            await q.message.reply_text("❌ Admin only")
            return

        text = "📊 ADMIN REPORT\n\n"
        for uid, d in user_data.items():
            text += f"{uid}: {d}\n"

    await q.message.reply_text(text, reply_markup=menu(int(user_id)))

# ================= MAIN =================
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot running...")

    async def post_init(app):
        await app.bot.delete_webhook(drop_pending_updates=True)

        scheduler = AsyncIOScheduler()
        scheduler.add_job(send_daily_report, "cron", hour=8, minute=0, args=[app])
        scheduler.start()

    app.post_init = post_init

    app.run_polling()

# ================= RUN =================
if __name__ == "__main__":
    main()
          