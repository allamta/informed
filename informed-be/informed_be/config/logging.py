import logging
import sys

from informed_be.config.settings import settings


def setup_logging() -> None:
    """Configure logging for the application. Call once at startup.

    Reads LOG_LEVEL from settings (environment variable).
    """
    level = settings.LOG_LEVEL.upper()
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logging.getLogger(__name__).info(f"Logging configured at {level} level")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)
