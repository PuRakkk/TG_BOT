from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardRemove
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardRemove
from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler
import requests
import json
import nest_asyncio
import asyncio
from datetime import datetime
import psycopg2

TK = "7961288559:AAE6hwpisp77F-e1lLAEmtY15PyAGrIS8Eo"

WEBHOOK_URL = "https://ezzecore1.mobi:8444/qrjump-bot"

TELEGRAM_URL = f"https://api.telegram.org/bot{TK}/setWebhook?url={WEBHOOK_URL}"

DB_HOST = "localhost"
DB_NAME = "ezzeqr_db"
DB_USER = "PuRak"
DB_PASS = "chessmandb987"

global_date = datetime.now()

# Set up logging
logging.basicConfig(
    filename='bot_log.txt',  # Log file location
    level=logging.DEBUG,      # Log all levels (DEBUG and above)
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def set_command(user_language):
    try:
        if user_language == "Khmer":
            base_language = {
                'start_desc': 'ចុច Start ដើម្បីចាប់ផ្តើម bot',
                'qrjump_desc': 'ទៅកាន់កម្មវិធី QR Jump',
                'change_language_desc': 'ផ្លាស់ប្តូរភាសា',
                'share_contact_desc': 'ចែករំលែកទំនាក់ទំនង',
                'help_desc': 'ជំនួយ'
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
                'start_desc': 'Start the bot',
                'qrjump_desc': 'Go to QR Jump miniapp',
                'change_language_desc': 'Change language',
                'share_contact_desc': 'Share contact information',
                'help_desc': 'Get help'
            }

        user_command = [
            {'command': 'start', 'description': base_language["start_desc"]},
            {'command': 'qrjump', 'description': base_language["qrjump_desc"]},
            {'command': 'change_language', 'description': base_language["change_language_desc"]},
            {'command': 'share_contact', 'description': base_language["share_contact_desc"]},
            {'command': 'help', 'description': base_language["help_desc"]}
        ]

        data = {'commands': user_command}
        url = f"https://api.telegram.org/bot{TK}/setMyCommands"
        response = requests.post(url, json=data)

        if response.status_code == 200:
            logging.info("Commands set successfully!")
        else:
            logging.error(f"Failed to set commands. HTTP Code: {response.status_code}. Response: {response.text}")

    except Exception as e:
        logging.error(f"Error in set_command function: {e}")

def set_webhook():
    try:
        response = requests.get(TELEGRAM_URL)
        logging.info(f"Webhook set successfully: {response.json()}")
        return response.json()
    except Exception as e:
        logging.error(f"Error setting webhook: {e}")
        return None

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

    try:
        db_connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS)
        cursor = db_connection.cursor()

        fetch_tgid_script = """SELECT telegram_id, user_status, user_choose_language FROM qrjump_users_storage WHERE telegram_id = %s"""
        cursor.execute(fetch_tgid_script, (telegram_id,))
        result_query = cursor.fetchone()

        db_connection.commit()

    except psycopg2.Error as e:
        logging.error(f"Database error in start command: {e}")
    finally:
        cursor.close()

    if result_query:
        verify_telegram_id, verify_user_status, verify_user_choose_language = result_query
    else:
        verify_telegram_id, verify_user_status, verify_user_choose_language = None, None, None

    if verify_telegram_id == telegram_id and verify_user_status == 1 and verify_user_choose_language == "English":
        set_command(verify_user_choose_language)
        await update.message.reply_text(f"Welcome, {full_name} Glad to have you here!", reply_markup=ReplyKeyboardRemove())
        logging.info(f"User {full_name} (ID: {telegram_id}) successfully logged in (English).")

    elif verify_telegram_id == telegram_id and verify_user_status == 1 and verify_user_choose_language == "Khmer":
        set_command(verify_user_choose_language)
        await update.message.reply_text(f"សូមស្វាគមន៍, {full_name} រីករាយដែលបានជួបអ្នក!", reply_markup=ReplyKeyboardRemove())
        logging.info(f"User {full_name} (ID: {telegram_id}) successfully logged in (Khmer).")

    elif verify_telegram_id == telegram_id and verify_user_status == 0:
        await update.message.reply_text("You got banned from the bot")
        logging.warning(f"User {full_name} (ID: {telegram_id}) banned from bot.")

    elif result_query == None:
        set_command("English")
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
    try:
        db_connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS)
        
        cursor = db_connection.cursor()

        fetch_tgid_script = """SELECT user_choose_language FROM qrjump_users_storage WHERE telegram_id = %s"""

        cursor.execute(fetch_tgid_script, (telegram_id,))

        result_query = cursor.fetchone()

    except psycopg2.Error as e: 
        print(e)

    finally:
        cursor.close()

    en_button = KeyboardButton("🇬🇧 English")
    kh_button = KeyboardButton("🇰🇭 Khmer")

    language_keyboard_button = [[en_button, kh_button]]

    language_reply_remark = ReplyKeyboardMarkup(language_keyboard_button, resize_keyboard=True, one_time_keyboard=True)

    if result_query[0] == "English":
        await update.message.reply_text("Please choose your language:",reply_markup=language_reply_remark)

    elif result_query[0] == "Khmer":
        await update.message.reply_text("សូមជ្រើសរើសភាសារបស់អ្នក:",reply_markup=language_reply_remark)
    else:
        await update.message.reply_text("Please choose your language",reply_markup=language_reply_remark)


async def language_choice(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:

    user_choice = update.message.text
    user = update.effective_user
    telegram_id = user.id

    if user_choice == "🇬🇧 English":

        try:
            db_connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS)
            
            cursor = db_connection.cursor()

            update_script = "UPDATE qrjump_users_storage SET user_choose_language = 'English' WHERE telegram_id = %s"

            cursor.execute(update_script, (telegram_id,))


            fetch_script = "SELECT phone_number FROM qrjump_users_storage WHERE telegram_id = %s"

            cursor.execute(fetch_script, (telegram_id,))

            result = cursor.fetchone()

            db_connection.commit()
        except psycopg2.Error as e:
            print(e)

        finally:
            cursor.close()

        set_command("English")

        if result and result[0]:
            await update.message.reply_text("You have selected English 🇬🇧", reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text("You have selected English 🇬🇧", reply_markup=ReplyKeyboardRemove())
            await share_contact_question(update,context)

    elif user_choice == "🇰🇭 Khmer":

        try:
            db_connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS)
            
            cursor = db_connection.cursor()

            update_script = "UPDATE qrjump_users_storage SET user_choose_language = 'Khmer' WHERE telegram_id = %s"

            cursor.execute(update_script, (telegram_id,))

            fetch_script = "SELECT phone_number FROM qrjump_users_storage WHERE telegram_id = %s"

            cursor.execute(fetch_script, (telegram_id,))

            result = cursor.fetchone()

            db_connection.commit()
        except psycopg2.Error as e:
            print(e)

        finally:
            cursor.close()

        set_command("Khmer")
        
        if result and result[0]:
            await update.message.reply_text("អ្នកបានជ្រើសរើសភាសាខ្មែរ 🇰🇭", reply_markup=ReplyKeyboardRemove())
        else:
            await update.message.reply_text("អ្នកបានជ្រើសរើសភាសាខ្មែរ 🇰🇭", reply_markup=ReplyKeyboardRemove())
            await share_contact_question(update,context)
    else:
        await update.message.reply_text("សូមជ្រើសរើសភាសាដែលត្រឹមត្រូវ Please choose a valid language.")

async def share_contact_question(update:Update,context:ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    telegram_id = user.id
    try:
        db_connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS)
        
        cursor = db_connection.cursor()

        fetch_tgid_script = """SELECT user_choose_language FROM qrjump_users_storage WHERE telegram_id = %s"""

        cursor.execute(fetch_tgid_script, (telegram_id,))

        result_query = cursor.fetchone()

    except psycopg2.Error as e: 
        print(e)

    finally:
        cursor.close()

    if result_query and result_query[0] == "English":
        yes_button = InlineKeyboardButton("✅ Yes", callback_data='yes')
        no_button = InlineKeyboardButton("❌ No", callback_data='no')
        question_text = "Would you like to share your contact?"
    elif result_query and result_query[0] == "Khmer":
        yes_button = InlineKeyboardButton("✅ បាទ/ចាស់", callback_data='yes')
        no_button = InlineKeyboardButton("❌ ទេ", callback_data='no')
        question_text = "តើអ្នកចង់ចែករំលែកទំនាក់ទំនងរបស់អ្នកឬទេ?"
    else:
        await update.message.reply_text("Error: Unable to determine language.")
        return
    
    yes_no_keyboard = [[yes_button, no_button]]
    reply_markup = InlineKeyboardMarkup(yes_no_keyboard)
    await update.message.reply_text(question_text, reply_markup=reply_markup)

async def share_contact(update:Update, context:ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        telegram_id = user.id
        try:
            db_connection = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS)
            
            cursor = db_connection.cursor()

            fetch_tgid_script = """SELECT user_choose_language, phone_number FROM qrjump_users_storage WHERE telegram_id = %s"""

            cursor.execute(fetch_tgid_script, (telegram_id,))

            result_query = cursor.fetchone()


        except psycopg2.Error as e: 
            print(e)

        finally:
            cursor.close()

        if result_query[0] == "English":
            
            if query.data == 'yes':
                share_en_contact_btn = KeyboardButton("📞Share your contact", request_contact=True)
                share_en_contact_btn_keyboard = [[share_en_contact_btn]]
                share_en_contact_reply_markup = ReplyKeyboardMarkup(share_en_contact_btn_keyboard, resize_keyboard=True, one_time_keyboard=True)
                await update.callback_query.message.reply_text("Please share your contact information.", 
                reply_markup=share_en_contact_reply_markup)

            elif query.data == 'no':
                await update.callback_query.message.reply_text("You have chosen not to share your contact.", reply_markup=ReplyKeyboardRemove())

        elif result_query[0] == "Khmer":

            if query.data == 'yes':
                share_en_contact_btn = KeyboardButton("📞ផ្តល់ព័ត៌មានទំនាក់ទំនង", request_contact=True)
                share_en_contact_btn_keyboard = [[share_en_contact_btn]]
                share_en_contact_reply_markup = ReplyKeyboardMarkup(share_en_contact_btn_keyboard, resize_keyboard=True, one_time_keyboard=True)
                await update.callback_query.message.reply_text("សូមចែករំលែកព័ត៌មានទំនាក់ទំនងរបស់អ្នក", reply_markup=share_en_contact_reply_markup)

            elif query.data == 'no':
                await update.callback_query.message.reply_text("អ្នកបានជ្រើសរើសមិនចែករំលែកព័ត៌មានទំនាក់ទំនង។ សូមអរគុណ។", reply_markup=ReplyKeyboardRemove())
    
async def process_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    contact = update.message.contact

    user = update.effective_user

    telegram_id = user.id
    try:
        db_connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS)
        
        cursor = db_connection.cursor()

        fetch_tgid_script = """SELECT user_choose_language FROM qrjump_users_storage WHERE telegram_id = %s"""

        cursor.execute(fetch_tgid_script, (telegram_id,))

        result_query = cursor.fetchone()


    except psycopg2.Error as e: 
        print(e)

    finally:
        cursor.close()

    phone_number = contact.phone_number
    first_name = contact.first_name
    last_name = contact.last_name if contact.last_name else ""
    username = update.effective_user.username if update.effective_user.username else "Not provided"

    if result_query[0] == "English":
        response = (
        f"Thanks for sharing your contact!\n"
        f"Full Name: {first_name} {last_name}\n"
        f"Phone Number: {phone_number}\n"
        f"Username: https://t.me/{username}"
    )

    elif result_query[0] == "Khmer":
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
    try:
        db_connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS)
        
        cursor = db_connection.cursor()

        fetch_tgid_script = """SELECT user_choose_language FROM qrjump_users_storage WHERE telegram_id = %s"""

        cursor.execute(fetch_tgid_script, (telegram_id,))

        result_query = cursor.fetchone()

    except psycopg2.Error as e: 
        print(e)

    finally:
        cursor.close()


    keyboard = [[InlineKeyboardButton("NEXT", web_app=WebAppInfo(url="https://ezzecore1.mobi:444?v1.1"))]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_khmer_message = """QRJump ធ្វើប្រតិបត្តិការលឿន សុវត្ថិភាព និងងាយស្រួលដោយប្រើកូដ QR ។ មិនថាអ្នកធ្វើការផ្ញើប្រាក់ ធ្វើការទូទាត់ទេ QRJUMP សម្រួលជាជម្រើសដ៏ល្អសម្រាប់អ្នក"""
    welcome_english_message = """QRJump makes transactions fast, secure, and easy using QR codes. Whether you're sending money, making payments, QRJUMP simplifies the process for you."""
    if result_query[0] == "Khmer":
        if update.callback_query:
            await update.callback_query.message.reply_text("សូមស្វាគមន៏មកកាន់​​ QRJump!",reply_markup=ReplyKeyboardRemove())
            await update.callback_query.message.reply_text(welcome_khmer_message,reply_markup=reply_markup)
            await update.callback_query.answer()
        elif update.message:
            await update.message.reply_text("សូមស្វាគមន៏មកកាន់​​ QRJump!",reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text(welcome_khmer_message, reply_markup=reply_markup)

    elif result_query[0] == "English":
        if update.callback_query:
            await update.callback_query.message.reply_text("Welcome to QRJump!",reply_markup=ReplyKeyboardRemove())
            await update.callback_query.message.reply_text(welcome_english_message, reply_markup=reply_markup)
            await update.callback_query.answer()
        elif update.message:
            await update.message.reply_text("Welcome to QRJump!",reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text(welcome_english_message, reply_markup=reply_markup) 

async def get_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user

    telegram_id = user.id
    try:
        db_connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS)
        
        cursor = db_connection.cursor()

        fetch_tgid_script = """SELECT user_choose_language FROM qrjump_users_storage WHERE telegram_id = %s"""

        cursor.execute(fetch_tgid_script, (telegram_id,))

        result_query = cursor.fetchone()


    except psycopg2.Error as e: 
        print(e)

    finally:
        cursor.close()

    if result_query[0] == "English":
        await update.message.reply_text("Comming soon",reply_markup=ReplyKeyboardRemove())
    
    elif result_query[0] == "Khmer":
        await update.message.reply_text("នឹងមានក្នុងពេលឆាប់ៗនេះ",reply_markup=ReplyKeyboardRemove())


async def main():
    app = Application.builder().token(TK).build()

    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("qrjump",website))
    app.add_handler(CommandHandler("change_language",language_btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, language_choice))
    app.add_handler(CommandHandler("share_contact",share_contact_question))
    app.add_handler(CallbackQueryHandler(share_contact, pattern="^yes$"))
    app.add_handler(CallbackQueryHandler(share_contact, pattern="^no$"))
    app.add_handler(MessageHandler(filters.CONTACT, process_contact))
    app.add_handler(CommandHandler("help",get_help))

    await app.run_polling()

if __name__ == '__main__':

    nest_asyncio.apply()

    set_webhook()

    asyncio.run(main())