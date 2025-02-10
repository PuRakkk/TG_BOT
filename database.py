DB_HOST = "localhost"
DB_NAME = "ezzeqr_db"
DB_USER = "PuRak"
DB_PASS = "chessmandb987"


TK = "7659326826:AAEUrUmsC0sbl92zR8LDC7vzBOyY9ULCgV4"

WEBHOOK_URL = "https://ezzecore1.mobi:8444/qrjump-bot"

TELEGRAM_URL = f"https://api.telegram.org/bot{TK}/setWebhook?url={WEBHOOK_URL}"

FETCH_USER_INFORMATION = """SELECT telegram_id, user_status, user_choose_language, phone_number, user_pin FROM qrjump_users_storage WHERE telegram_id = %s"""