import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_file: Optional[Path] = None,
    max_bytes: int = 10_485_760,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Configure logging for the application.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format: Log message format
        log_file: Optional path to log file. If provided, logs will be written to file
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
    """
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(logging.Formatter(format))
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=level, format=format, handlers=handlers)

    # Set levels for third-party packages
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("aiohttp").setLevel(logging.INFO)

    # Create our application logger
    logger = logging.getLogger("status_tiles")
    logger.setLevel(level)

    # Log startup information
    logger.info(f"Logging configured with level: {level}")
    if log_file:
        logger.info(f"Logging to file: {log_file}")
