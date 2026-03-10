import sys
from loguru import logger
from app.core.config import settings

def setup_logging():
    # Remove default handler
    logger.remove()

    # Define log format based on environment
    if settings.ENVIRONMENT == "prod":
        # Structured JSON logging for production
        logger.add(
            sys.stdout,
            format="{message}",
            serialize=True,
            level="INFO",
            backtrace=True,
            diagnose=False,
        )
    else:
        # Human-readable colors for dev
        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level="DEBUG",
        )

    return logger
