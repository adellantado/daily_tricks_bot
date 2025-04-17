import logging
import asyncio
import os
import random
from datetime import datetime, time as dt_time

import openai
from dotenv import load_dotenv
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackContext, \
    MessageHandler, filters
from telegram.constants import ParseMode
import re

# Load environment variables
load_dotenv()
logging.basicConfig(
    filename='bot.log',
    filemode='a',
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Initialize OpenAI client
openai.api_key = os.getenv('OPENAI_API_KEY')

# Initialize Telegram bot
bot = Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
python_channel_id = os.getenv('PYTHON_CHANNEL_ID')
trader_channel_id = os.getenv('TRADER_CHANNEL_ID')
owner_id = int(os.getenv('OWNER_ID'))


def generate_python_tip():
    """Generate a daily Python tip using OpenAI."""
    try:
        level = random.choice(["Professional", "Basic", "Advanced"])
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Daily Python Tricks channel. "
                        "Format your response in this exact structure:\n"
                        "1. Start with the level in bold: *Level: #Basic* or *Level: #Advanced* or *Level: #Professional*\n"
                        "2. Add a brief explanation of the tip in bold and then the next line.\n"
                        "3. Always include a code example using this exact format:\n"
                        "```python\n"
                        "# Your code here\n"
                        "# Add comments with output if needed\n"
                        "```\n"
                        "4. Do not add any additional text after the code example\n"
                        "5. Make sure code examples are practical and executable\n"
                        "6. Use proper Python formatting and indentation in code examples\n"
                        "7. Use emojis extensively in the text\n"
                        "8. Do not repeat the same tip"
                    )
                },
                {
                    "role": "user",
                    "content": f"Give me today's {level} Python tip."
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating Python tip: {e}")
        return None

def generate_trader_tip():
    """Generate a daily trading tip using OpenAI."""
    try:
        level = random.choice(["Professional", "Basic", "Advanced"])
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Daily Trading Tips channel. "
                        "Format your response in this exact structure:\n"
                        "1. Start with the level in bold: *Level: #Basic* or *Level: #Advanced* or *Level: #Professional*\n"
                        "2. Add a brief explanation of the trading concept, strategy, or tip in bold\n"
                        "3. Provide practical examples or scenarios\n"
                        "4. Include relevant trading terminology\n"
                        "5. Add risk management considerations if applicable\n"
                        "6. Use emojis extensively in the text\n"
                        "7. Do not repeat the same tip\n"
                        "8. Keep it concise and practical"
                    )
                },
                {
                    "role": "user",
                    "content": f"Give me today's {level} trading tip."
                }
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating trader tip: {e}")
        return None

def escape_markdown(text):
    """Handle Telegram markdown formatting for pre-escaped text."""
    # First unescape any pre-escaped characters
    text = text.replace('\\*', '*')
    text = text.replace('\\`', '`')
    
    # Now escape special characters for Telegram MarkdownV2
    special_chars = ['_', '[', ']', '(', ')', '~', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

async def send_python_tip():
    """Send the generated Python tip to the Python channel."""
    tip = generate_python_tip()
    if tip:
        try:
            message = escape_markdown(tip)
            await bot.send_message(
                chat_id=python_channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            logger.info("Python tip sent successfully!")
        except Exception as e:
            logger.error(f"Error sending Python tip: {e}")

async def send_trader_tip():
    """Send the generated trading tip to the trader channel."""
    tip = generate_trader_tip()
    if tip:
        try:
            message = escape_markdown(tip)
            await bot.send_message(
                chat_id=trader_channel_id,
                text=message,
                parse_mode=ParseMode.MARKDOWN_V2
            )
            logger.info("Trader tip sent successfully!")
        except Exception as e:
            logger.error(f"Error sending trader tip: {e}")

async def test_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /test command."""
    if update.effective_user.id != owner_id:
        await update.message.reply_text("Sorry, this command is only available to the bot owner.")
        return
    
    # Get the type of tip to test from the command arguments
    tip_type = context.args[0] if context.args else "python"
    
    if tip_type.lower() == "python":
        tip = generate_python_tip()
    elif tip_type.lower() == "trader":
        tip = generate_trader_tip()
    else:
        await update.message.reply_text("Please specify 'python' or 'trader' after /test")
        return
    
    if tip:
        message = escape_markdown(tip)
        await update.message.reply_text(
            text=message,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    else:
        await update.message.reply_text("Sorry, there was an error generating the tip.")

async def id_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /id command to get chat ID."""
    # Check if the user is the owner
    if update.effective_user.id != owner_id:
        await update.message.reply_text("Sorry, this command is only available to the bot owner.")
        return
    
    try:
        # Get the chat ID
        chat_id = update.effective_chat.id
        chat_type = update.effective_chat.type
        chat_title = update.effective_chat.title if update.effective_chat.title else "Private Chat"
        
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
    application = Application.builder().token(os.getenv('TELEGRAM_BOT_TOKEN')).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("test", test_command))
    application.add_handler(CommandHandler("id", id_command))
    application.add_handler(MessageHandler(filters.ALL, all_handler))
    
    # Start the bot with polling
    logger.info("Bot started! Waiting for scheduled tasks...")
    application.run_polling()

if __name__ == "__main__":
    main()