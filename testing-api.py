import logging
import asyncio
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import nest_asyncio
import uvicorn
from fastapi.responses import JSONResponse

# Setup logging
logging.basicConfig(level=logging.INFO)

# Set your token, port, and webhook URL
TK = "7659326826:AAEUrUmsC0sbl92zR8LDC7vzBOyY9ULCgV4"
PORT = 8443
WEBHOOK_URL = "https://b8be-110-235-223-133.ngrok-free.app/qrjump-bot"

app = FastAPI()
bot_app = None  # Global bot application instance

@app.post("/qrjump-bot")
async def webhook(request: Request):
    update_data = await request.json()
    logging.info(f"Received update: {update_data}")
    
    if bot_app:
        try:
            update = Update.de_json(update_data, bot_app.bot)
            await bot_app.update_queue.put(update)
            logging.info("Update forwarded to bot application")
        except Exception as e:
            logging.error(f"Error processing update: {e}")
    
    return JSONResponse(content={"status": "ok"})

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logging.info(f"Start command from {user.first_name}")
    await update.message.reply_text("Hello, I'm working now!")

async def setup_bot():
    global bot_app
    bot_app = (
        Application.builder()
        .token(TK)
        .build()
    )
    
    # Add handlers
    bot_app.add_handler(CommandHandler("start", start))
    
    # Set webhook ONCE
    await bot_app.bot.set_webhook(WEBHOOK_URL)
    logging.info("Webhook configured successfully")

    # Start the bot application (but don't run the built-in web server)
    await bot_app.initialize()
    await bot_app.start()

async def shutdown():
    if bot_app:
        await bot_app.stop()
        await bot_app.shutdown()

if __name__ == '__main__':
    nest_asyncio.apply()
    
    # Create event loop
    loop = asyncio.get_event_loop()
    
    # Start bot setup first
    loop.run_until_complete(setup_bot())
    
    # Configure FastAPI server
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT)
    server = uvicorn.Server(config)
    
    try:
        logging.info("Starting server...")
        loop.run_until_complete(server.serve())
    finally:
        logging.info("Shutting down...")
        loop.run_until_complete(shutdown())