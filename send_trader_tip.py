import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from bot import send_trader_tip

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    filename='trader_tips.log',
    filemode='a',
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def send_tip():
    """Send Trading tip."""
    try:
        logger.info("Starting to send Trading tip...")
        await send_trader_tip()
        logger.info("Trading tip sent successfully")
    except Exception as e:
        logger.error(f"Error sending Trading tip: {e}")

if __name__ == "__main__":
    logger.info(f"Starting Trading tip script at {datetime.now()}")
    asyncio.run(send_tip())
    logger.info(f"Finished Trading tip script at {datetime.now()}") 