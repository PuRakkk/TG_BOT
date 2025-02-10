from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Multi-language command dictionary
commands = {
    "en": [
        ("start", "Start the bot"),
        ("help", "Show help information"),
        ("language", "Change the language"),
    ],
    "kh": [
        ("start", "ចាប់ផ្តើម"),
        ("help", "ការជួយ"),
        ("language", "ផ្លាស់ប្តូរភាសា"),
    ]
}

# Temporary in-memory store for user language preferences
user_language = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    chat_id = update.effective_chat.id
    lang = user_language.get(chat_id, "en")

    # Set the commands based on user language
    await context.bot.set_my_commands([BotCommand(*command) for command in commands[lang]])

    # Send the initial message with inline keyboard for language selection
    message = "Welcome! Use /language to change your language.\n\nPlease type /start to continue."
    if lang == "kh":
        message = "សូមស្វាគមន៍! ប្រើ /language ដើម្បីផ្លាស់ប្តូរភាសា។\n\nសូមវាយ /start ដើម្បីបន្ត។"

    # Send the message with the language selection menu
    await context.bot.send_message(chat_id, text=message, reply_markup=get_language_keyboard(chat_id))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /help command."""
    chat_id = update.effective_chat.id
    lang = user_language.get(chat_id, "en")
    message = "This is the help menu."
    if lang == "kh":
        message = "នេះគឺជាម៉ឺនុយជំនួយ។"
    
    # Send the help message with language options (persistent)
    await context.bot.send_message(chat_id, text=message, reply_markup=get_language_keyboard(chat_id))

async def language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /language command and show language options."""
    chat_id = update.effective_chat.id
    # Send the language options message, which will stay persistent
    await context.bot.send_message(chat_id, text="Please choose a language:", reply_markup=get_language_keyboard(chat_id))

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set the user's preferred language and update the menu."""
    query = update.callback_query
    await query.answer()  # Acknowledge the button press

    chat_id = query.message.chat.id
    data = query.data

    if data == "lang_en":
        lang = "en"
    elif data == "lang_kh":
        lang = "kh"
    else:
        await query.edit_message_text("Invalid choice.")
        return

    # Save the user's language preference
    user_language[chat_id] = lang

    # Update the bot menu dynamically after language change
    await context.bot.set_my_commands([BotCommand(*command) for command in commands[lang]])

    # Send the language update message and keep the language options persistent
    new_text = "Language updated! Please choose a language:"
    if lang == "kh":
        new_text = "ភាសាត្រូវបានធ្វើបច្ចុប្បន្នភាព! សូមជ្រើសរើសភាសា៖"

    # Edit the existing message with the new language text and options
    await query.edit_message_text(text=new_text, reply_markup=get_language_keyboard(chat_id))

    # Suggest the user to type `/start` to re-trigger the bot with the new language
    start_message = "Now that your language is set, type /start to see the changes!"
    if lang == "kh":
        start_message = "ឥឡូវនេះភាសារបស់អ្នកត្រូវបានកំណត់ហើយ។ សូមវាយ /start ដើម្បីមើលការផ្លាស់ប្តូរ!"

    await context.bot.send_message(chat_id, text=start_message)

def get_language_keyboard(chat_id):
    """Return a persistent language selection keyboard."""
    lang = user_language.get(chat_id, "en")
    return InlineKeyboardMarkup([ 
        [InlineKeyboardButton("English", callback_data="lang_en")], 
        [InlineKeyboardButton("Khmer", callback_data="lang_kh")] 
    ])

def main():
    """Main function to run the bot."""
    TOKEN = "7659326826:AAEUrUmsC0sbl92zR8LDC7vzBOyY9ULCgV4"  # Replace with your bot token

    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("language", language))

    # CallbackQueryHandler for language selection
    application.add_handler(CallbackQueryHandler(set_language))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()
