import asyncio
import logging
from datetime import datetime
import os
from dotenv import load_dotenv
from bot import send_js_tip

logger = logging.getLogger(__name__)


async def send_tip():
    """Send JavaScript/TypeScript tip."""
    try:
        logger.info("Starting to send JS/TS tip...")
        await send_js_tip()
        logger.info("JS/TS tip sent successfully")
    except Exception as e:
        logger.error(f"Error sending JS/TS tip: {e}")


if __name__ == "__main__":
    logger.info(f"Starting JS/TS tip script at {datetime.now()}")
    asyncio.run(send_tip())
    logger.info(f"Finished JS/TS tip script at {datetime.now()}")
