import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from bot import send_python_tip

logger = logging.getLogger(__name__)


async def send_tip():
    """Send Python tip."""
    try:
        logger.info("Starting to send Python tip...")
        await send_python_tip()
        logger.info("Python tip sent successfully")
    except Exception as e:
        logger.error(f"Error sending Python tip: {e}")


if __name__ == "__main__":
    logger.info(f"Starting Python tip script at {datetime.now()}")
    asyncio.run(send_tip())
    logger.info(f"Finished Python tip script at {datetime.now()}")
