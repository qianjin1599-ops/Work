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
        text = f"☕️ {name} Smoke Started (10 min limit)"

    elif query.data == "prayer":
        data["prayer_limit"] = now + timedelta(minutes=15)
        text = f"🙏 {name} Prayer Started (15 min limit)"

    elif query.data == "off":
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
            text += f"\n⚠️ Fine: {fines} PKR"

    # ================= MENU BUTTON =================
    elif query.data == "menu":
        text = "👨‍💼 Main Menu"

    # ================= KEYBOARD =================
    keyboard = [
        [InlineKeyboardButton("🟢 Start Work", callback_data="start_work")],
        [InlineKeyboardButton("🍔 Lunch", callback_data="lunch")],
        [InlineKeyboardButton("🚽 Washroom", callback_data="washroom")],
        [InlineKeyboardButton("☕️ Smoke", callback_data="smoke")],
        [InlineKeyboardButton("🙏 Prayer", callback_data="prayer")],
        [InlineKeyboardButton("💺 Back", callback_data="back")],
        [InlineKeyboardButton("🔴 Off", callback_data="off")],
        [InlineKeyboardButton("🏠 Menu", callback_data="menu")]
    ]

    await query.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )