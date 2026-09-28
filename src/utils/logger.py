import os
import sys
from loguru import logger


def get_logger(name: str):
    logger.remove()
    log_level = os.getenv("LOG_LEVEL", "INFO")
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
        level=log_level,
        colorize=True,
    )
    logger.add(
        f"logs/{name}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}",
        level=log_level,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
    )
    return logger.bind(name=name)
