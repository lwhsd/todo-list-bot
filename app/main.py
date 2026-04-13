import os
import logging
import traceback

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)
from config import BOT_TOKEN
from commands import COMMANDS
from scheduler import start_scheduler


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

_DROP_PENDING = os.getenv("ENV", "development") != "production"

async def _error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling update:\n%s", traceback.format_exc())
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "An internal error occurred. Please try again."
        )

async def _post_shutdown(app) -> None:
    logger.info("Bot shut down cleanly.")

async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome!!!")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).post_shutdown(_post_shutdown).build()
    app.add_handler(CommandHandler("start", start_handler))
    for cmd in COMMANDS:
        if cmd.handler_type == 'callback':
            app.add_handler(CallbackQueryHandler(cmd.handler, pattern="^clear_"))
        else:
            app.add_handler(CommandHandler(cmd.name, cmd.handler))


    app.add_error_handler(_error_handler)
    start_scheduler(app)
    
    app.run_polling(drop_pending_updates=_DROP_PENDING)

if __name__ == "__main__":
    main()