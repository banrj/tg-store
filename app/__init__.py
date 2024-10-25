import logging
import sys

from app.settings import settings

__all__ = [
    "settings",
]

console_log_stream = logging.StreamHandler(sys.stdout)
console_log_stream.setFormatter(
    logging.Formatter(
        '{asctime} {levelname:10} [{pathname} def {funcName}] ::: | {message}',
        style='{',
    )
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(console_log_stream)
