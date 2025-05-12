import logging
import os
from datetime import datetime, time as dt_time

import openai
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    CallbackContext,
    MessageHandler,
    filters,
)
from telegram.constants import ParseMode

from services.python_tips import PythonTips
from services.js_tips import JsTips
from services.trader_tips import TraderTips
from services.blockchain_tips import BlockchainTips

load_dotenv()
logging.basicConfig(
    filename="bot.log",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize Telegram bot
bot = Bot(token=os.getenv("TELEGRAM_BOT_TOKEN"))
python_channel_id = os.getenv("PYTHON_CHANNEL_ID")
trader_channel_id = os.getenv("TRADER_CHANNEL_ID")
js_channel_id = os.getenv("JS_CHANNEL_ID")
blockchain_channel_id = os.getenv("BLOCKCHAIN_CHANNEL_ID")
owner_id = int(os.getenv("OWNER_ID"))


async def generate_python_tip():
    try:
        return await PythonTips().get_unique_tip()
    except Exception as e:
        logger.error(f"Error generating Python tip: {e}")
        return None


async def generate_trader_tip():
    try:
        return await TraderTips().get_unique_tip()
    except Exception as e:
        logger.error(f"Error generating trader tip: {e}")
        return None


async def generate_js_tip():
    try:
        return await JsTips().get_unique_tip()
    except Exception as e:
        logger.error(f"Error generating JS/TS tip: {e}")
        return None


async def generate_blockchain_tip():
    try:
        return await BlockchainTips().get_unique_tip()
    except Exception as e:
        logger.error(f"Error generating blockchain tip: {e}")
        return None


def escape_markdown(text):
    """Handle Telegram markdown formatting for pre-escaped text."""
    # First unescape any pre-escaped characters
    text = text.replace("\\*", "*")
    text = text.replace("\\`", "`")

    # Now escape special characters for Telegram MarkdownV2
    special_chars = [
        "_",
        "[",
        "]",
        "(",
        ")",
        "~",
        ">",
        "#",
        "+",
        "-",
        "=",
        "|",
        "{",
        "}",
        ".",
        "!",
    ]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")

    return text


async def send_python_tip():
    tip = await generate_python_tip()
    if tip:
        try:
            message = escape_markdown(tip)
            await bot.send_message(
                chat_id=python_channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            logger.info("Python tip sent successfully!")
        except Exception as e:
            logger.error(f"Error sending Python tip: {e}")


async def send_trader_tip():
    tip = await generate_trader_tip()
    if tip:
        try:
            message = escape_markdown(tip)
            await bot.send_message(
                chat_id=trader_channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            logger.info("Trader tip sent successfully!")
        except Exception as e:
            logger.error(f"Error sending trader tip: {e}")


async def send_js_tip():
    tip = await generate_js_tip()
    if tip:
        try:
            message = escape_markdown(tip)
            await bot.send_message(
                chat_id=js_channel_id, text=message, parse_mode=ParseMode.MARKDOWN_V2
            )
            logger.info("JS/TS tip sent successfully!")
        except Exception as e:
            logger.error(f"Error sending JS/TS tip: {e}")


async def send_blockchain_tip():
    tip = await generate_blockchain_tip()
    if tip:
        try:
            message = escape_markdown(tip)
            await bot.send_message(
                chat_id=blockchain_channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            logger.info("Blockchain tip sent successfully!")
        except Exception as e:
            logger.error(f"Error sending blockchain tip: {e}")


async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /test command."""
    if update.effective_user.id != owner_id:
        await update.message.reply_text(
            "Sorry, this command is only available to the bot owner."
        )
        return

    # Get the type of tip to test from the command arguments
    tip_type = context.args[0] if context.args else "python"

    if tip_type.lower() == "python":
        tip = await generate_python_tip()
    elif tip_type.lower() == "trader":
        tip = await generate_trader_tip()
    elif tip_type.lower() == "blockchain":
        tip = await generate_blockchain_tip()
    elif tip_type.lower() in ["js", "javascript", "typescript"]:
        tip = await generate_js_tip()
    else:
        await update.message.reply_text(
            "Please specify 'python', 'trader', 'blockchain' or 'js' after /test"
        )
        return

    if tip:
        message = escape_markdown(tip)
        await update.message.reply_text(text=message, parse_mode=ParseMode.MARKDOWN_V2)
    else:
        await update.message.reply_text("Sorry, there was an error generating the tip.")


async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /id command to get chat ID."""
    # Check if the user is the owner
    if update.effective_user.id != owner_id:
        await update.message.reply_text(
            "Sorry, this command is only available to the bot owner."
        )
        return

    try:
        # Get the chat ID
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        chat_title = (
            update.effective_chat.title
            if update.effective_chat.title
            else "Private Chat"
        )

        message = f"💡 Chat Information:\n"
        message += f"Title: {chat_title}\n"
        message += f"Type: {chat_type}\n"
        message += f"ID: `{chat_id}`"

        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN_V2)
        logger.info(f"Chat ID information sent: {message}")
    except Exception as e:
        error_message = f"Error getting chat ID: {str(e)}"
        logger.error(error_message)
        await update.message.reply_text(error_message)


async def all_handler(update: Update, context: CallbackContext):
    logger.info(update.message)


def main():
    """Set up the application and start polling."""
    # Create the Application
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add command handlers
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(MessageHandler(filters.ALL, all_handler))

    # Start the bot with polling
    logger.info("Bot started! Waiting for scheduled tasks...")
    application.run_polling()


if __name__ == "__main__":
    main()
