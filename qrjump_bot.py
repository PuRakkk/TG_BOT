from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, BotCommand
import logging
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler,CallbackContext
import requests
import json
import nest_asyncio
import asyncio
from datetime import datetime
import psycopg2

DB_HOST = "localhost"
DB_NAME = "ezzeqr_db"
DB_USER = "purak"
DB_PASS = "chessmandb987"

TK = "7659326826:AAEUrUmsC0sbl92zR8LDC7vzBOyY9ULCgV4"

WEBHOOK_URL = "https://ezzecore1.mobi:8444/qrjump-bot"

TELEGRAM_URL = f"https://api.telegram.org/bot{TK}/setWebhook?url={WEBHOOK_URL}"

FETCH_USER_INFORMATION = """SELECT telegram_id, user_status, user_choose_language, phone_number FROM qrjump_users_storage WHERE telegram_id = %s"""

global_date = datetime.now()

logging.basicConfig(
    filename='bot_log.txt',
    level=logging.DEBUG, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def set_command(user_language,tg_id):
    app = Application.builder().token(TK).build()
    telegram_id = tg_id
    try:
        if user_language == "Khmer":
            base_language = {
                'qrjump_desc': 'ទៅកាន់កម្មវិធី QR Jump',
                'change_language_desc': 'ផ្លាស់ប្តូរភាសា',
                'share_contact_desc': 'ចែករំលែកទំនាក់ទំនង',
                'help_desc': 'ជំនួយ',
                'start_desc': 'ចុច Start ដើម្បីចាប់ផ្តើម bot'
            }

        elif user_language == "English":
            base_language = {
                'start_desc': 'Start the bot',
                'qrjump_desc': 'Go to QR Jump miniapp',
                'change_language_desc': 'Change language',
                'share_contact_desc': 'Share contact information',
                'help_desc': 'Get help'
            }

        else:
            base_language = {
                'qrjump_desc': 'Go to QR Jump miniapp',
                'change_language_desc': 'Change language',
                'share_contact_desc': 'Share contact information',
                'help_desc': 'Get help',
                'start_desc': 'Start the bot'
            }

        user_commands = [
            BotCommand("qrjump", base_language["qrjump_desc"]),
            BotCommand("change_language", base_language["change_language_desc"]),
            BotCommand("share_contact", base_language["share_contact_desc"]),
            BotCommand("help", base_language["help_desc"]),
            BotCommand("start", base_language["start_desc"]),
        ]

        await app.bot.set_my_commands(user_commands)
        logging.info("Commands updated successfully!")
    except Exception as e:
        logging.error(f"Error updating commands: {e}")

def set_webhook():
    try:
        response = requests.get(TELEGRAM_URL)
        logging.info(f"Webhook set successfully: {response.json()}")
        return response.json()
    except Exception as e:
        logging.error(f"Error setting webhook: {e}")
        return None

def fetch_language(telegramId):
    telegram_id = telegramId
    try:
        db_connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS)
        
        cursor = db_connection.cursor()

        fetch_tgid_script = FETCH_USER_INFORMATION

        cursor.execute(fetch_tgid_script, (telegram_id,))

        result_query = cursor.fetchone()

    except psycopg2.Error as e: 
        print(e)

    finally:
        cursor.close()
        return result_query if result_query else None

def update_users_language(telegramId,user_language):
    telegram_id = telegramId
    language = user_language
    try:
        db_connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS)
        
        cursor = db_connection.cursor()

        update_script = f"UPDATE qrjump_users_storage SET user_choose_language = '{language}' WHERE telegram_id = %s"

        cursor.execute(update_script, (telegram_id,))

        db_connection.commit()
    except psycopg2.Error as e:
        print(e)

    finally:
        cursor.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    telegram_id = user.id
    first_name = user.first_name
    last_name = user.last_name or ""
    full_name = first_name + " " + last_name
    username = user.username
    telegram_language = user.language_code
    visiter = "Human" if not user.is_bot else "Bot"
    created_at = global_date.strftime("%Y-%m-%d %H:%M")
    user_status = 1

    logging.info(f"Start command initiated by {full_name} (ID: {telegram_id})")

    result = fetch_language(telegram_id)

    if result:  
        verify_telegram_id = result[0]
        verify_user_status =  result[1]
        verify_user_choose_language = result[2]
    else:
        verify_telegram_id, verify_user_status, verify_user_choose_language = None, None, None

    if verify_telegram_id == telegram_id and verify_user_status == 1 and verify_user_choose_language == "English":
        await update.message.reply_text(f"Welcome, {full_name} Glad to have you here!", reply_markup=ReplyKeyboardRemove())
        logging.info(f"User {full_name} (ID: {telegram_id}) successfully logged in (English).")

    elif verify_telegram_id == telegram_id and verify_user_status == 1 and verify_user_choose_language == "Khmer":
        await update.message.reply_text(f"សូមស្វាគមន៍, {full_name} រីករាយដែលបានជួបអ្នក!", reply_markup=ReplyKeyboardRemove())
        logging.info(f"User {full_name} (ID: {telegram_id}) successfully logged in (Khmer).")

    elif verify_telegram_id == telegram_id and verify_user_status == 0:
        await update.message.reply_text("You got banned from the bot")
        logging.warning(f"User {full_name} (ID: {telegram_id}) banned from bot. Please contact Admin:@Chon_sarak")

    elif result == None or result[2] == None:
        await set_command("English",telegram_id)
        try:
            db_connection = psycopg2.connect(
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASS)
            cursor = db_connection.cursor()

            insert_script = """INSERT INTO qrjump_users_storage (telegram_id, first_name, last_name, full_name, username, telegram_language, user_status, created_at, visiter) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cursor.execute(insert_script, (telegram_id, first_name, last_name, full_name, username, telegram_language, user_status, created_at, visiter))

            db_connection.commit()
        except psycopg2.Error as e:
            logging.error(f"Database error during user registration: {e}")
        finally:
            cursor.close()

        await update.message.reply_text("Welcome to the bot! You can interact with me now.")
        logging.info(f"New user {full_name} (ID: {telegram_id}) registered.")
        await language_btn(update, context)

async def language_btn(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:

    user = update.effective_user

    telegram_id = user.id
    
    result = fetch_language(telegram_id)

    if result[1] == 1:
        en_button = KeyboardButton("🇬🇧 English")
        kh_button = KeyboardButton("🇰🇭 Khmer")

        language_keyboard_button = [[en_button, kh_button]]

        language_reply_remark = ReplyKeyboardMarkup(language_keyboard_button, resize_keyboard=True, one_time_keyboard=True)

        if result[2] == "English":
            await update.message.reply_text("Please choose your language:",reply_markup=language_reply_remark)

        elif result[2] == "Khmer":
            await update.message.reply_text("សូមជ្រើសរើសភាសារបស់អ្នក:",reply_markup=language_reply_remark)
        else:
            await update.message.reply_text("Please choose a valid language",reply_markup=language_reply_remark)
    elif result[1] == 0:
        return


async def language_choice(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:

    user_choice = update.message.text
    user = update.effective_user
    first_name = user.first_name
    last_name = user.last_name or ""
    full_name = first_name + " " + last_name
    telegram_id = user.id

    if user_choice == "🇬🇧 English":
        language = "English"
        result = fetch_language(telegram_id)

        if result[2] == None:
            await update.message.reply_text("You have selected English 🇬🇧", reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text(f"Welcome {full_name} to QR Jump! Please choose in Menu")
        elif result[2] == "English":
            await set_command("English",telegram_id)
            await update.message.reply_text("You have selected English 🇬🇧", reply_markup=ReplyKeyboardRemove())
        else:
            await set_command("English",telegram_id)
            await update.message.reply_text("You have selected English 🇬🇧", reply_markup=ReplyKeyboardRemove())

        update_users_language(telegram_id,language)

    elif user_choice == "🇰🇭 Khmer":
        language = "Khmer"

        result = fetch_language(telegram_id)
        
        if result[2] == None:
            await update.message.reply_text("អ្នកបានជ្រើសរើសភាសាខ្មែរ 🇰🇭", reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text(f"សូមស្វាគមន៏​ {full_name} មកកាន់​​ QRJump! សូមជ្រើសរើសក្នុងមីនុយ ឬ Menu")
        elif result[2] == "Khmer":
            await set_command("Khmer",telegram_id)
            await update.message.reply_text("អ្នកបានជ្រើសរើសភាសាខ្មែរ 🇰🇭", reply_markup=ReplyKeyboardRemove())
        else:
            await set_command("Khmer",telegram_id)
            await update.message.reply_text("អ្នកបានជ្រើសរើសភាសាខ្មែរ 🇰🇭", reply_markup=ReplyKeyboardRemove())
        update_users_language(telegram_id,language)
    else:
        await update.message.reply_text("Unknown Command")


async def share_contact(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:

        user = update.effective_user
        telegram_id = user.id
        result = fetch_language(telegram_id)

        if result[3] is None:
            if result[1] == 1:
                share_contact_btn = None
                if result[2] == "English":
                    share_contact_btn = KeyboardButton("📞Share your contact", request_contact=True)
                elif result[2] == "Khmer":
                    share_contact_btn = KeyboardButton("📞ផ្តល់ព័ត៌មានទំនាក់ទំនង", request_contact=True)

                if share_contact_btn:
                    share_contact_keyboard = [[share_contact_btn]]
                    share_contact_reply_markup = ReplyKeyboardMarkup(
                        share_contact_keyboard, resize_keyboard=True, one_time_keyboard=True
                    )
                    await update.message.reply_text(
                        "Please share your contact" if result[2] == "English" else "សូមចែករំលែកព័ត៌មានទំនាក់ទំនងរបស់អ្នក",
                        reply_markup=share_contact_reply_markup)
            elif result[1] == 0:
                    return
        elif result:
            await update.message.reply_text("You are already shared contact" if result[2] == "English" else "អ្នកបានចែករំលែកទំនាក់ទំនងរួចហើយ")
            

async def process_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contact = update.message.contact

    user = update.effective_user

    telegram_id = user.id
    
    result = fetch_language(telegram_id)  

    phone_number = contact.phone_number
    first_name = contact.first_name
    last_name = contact.last_name if contact.last_name else ""
    username = update.effective_user.username if update.effective_user.username else "Not provided"

    if result[2] == "English":
        await set_command("English",telegram_id)
        response = (
        f"Thanks for sharing your contact!\n"
        f"Full Name: {first_name} {last_name}\n"
        f"Phone Number: {phone_number}\n"
        f"Username: https://t.me/{username}"
    )

    elif result[2] == "Khmer":
        await set_command("Khmer",telegram_id)
        response = (
        f"អរគុណសម្រាប់ការចែករំលែកទំនាក់ទំនងរបស់អ្នក!\n"
        f"ឈ្មោះរបស់អ្នក: {first_name} {last_name}\n"
        f"លេខទូរស័ព្ទ: {phone_number}\n"
        f"ឈ្មោះអ្នកប្រើប្រាស់: https://t.me/{username}"
    )
    await update.message.reply_text(response, reply_markup=ReplyKeyboardRemove())
    
    try:
        db_connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS)
        
        cursor = db_connection.cursor()

        update_script = "UPDATE qrjump_users_storage SET phone_number = %s WHERE telegram_id = %s"

        cursor.execute(update_script, (phone_number,telegram_id,))

        db_connection.commit()
    except psycopg2.Error as e:
        print(e)

    finally:
        cursor.close()
    
async def website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    telegram_id = user.id

    print(telegram_id)

    result = fetch_language(telegram_id)

    keyboard = [[InlineKeyboardButton("NEXT", web_app=WebAppInfo(url=f"https://dd4f-175-100-10-23.ngrok-free.app?telegram_id={telegram_id}"))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_khmer_message = """សូមចុចលើ NEXT ដើម្បីចូលទៅ QR Jump"""
    welcome_english_message = """Please click on NEXT to go to QR Jump"""
    
    if result[1] == 1:
            if result[2] == "Khmer":
                if update.callback_query:
                    await update.callback_query.message.reply_text(welcome_khmer_message,reply_markup=reply_markup)
                    await update.callback_query.answer()
                elif update.message:
                    await update.message.reply_text(welcome_khmer_message, reply_markup=reply_markup)

            elif result[2] == "English":
                if update.callback_query:
                    await update.callback_query.message.reply_text(welcome_english_message, reply_markup=reply_markup)
                    await update.callback_query.answer()
                elif update.message:
                    await update.message.reply_text(welcome_english_message, reply_markup=reply_markup) 

    elif result[1] == 0:
        return

async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    telegram_id = user.id
    firstname = user.first_name or ""
    lastname = user.last_name or ""
    fullname = firstname + " " + lastname

    result = fetch_language(telegram_id)

    if result[1] == 1:
        if result[2] == "English":
            await update.message.reply_text(f"Welcome to admin! What can I help you, {fullname} \n Admin: @Sarak_chon",reply_markup=ReplyKeyboardRemove())
        
        elif result[2] == "Khmer":
            await update.message.reply_text(f"សូមស្វាគមន៍មកកាន់ admin! តើខ្ញុំអាចជួយអ្នកអ្វីខ្លះ, {fullname} \n Admin: @Sarak_chon",reply_markup=ReplyKeyboardRemove())
    elif result[1] == 0:
        return

async def main():
    app = Application.builder().token(TK).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("qrjump",website))
    app.add_handler(CommandHandler("change_language",language_btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, language_choice))
    app.add_handler(CommandHandler("share_contact",share_contact))
    app.add_handler(MessageHandler(filters.CONTACT, process_contact))
    app.add_handler(CommandHandler("help",get_help))

    await app.run_polling()

if __name__ == '__main__':

    nest_asyncio.apply()

    set_webhook()

    asyncio.run(main())