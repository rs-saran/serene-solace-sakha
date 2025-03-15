import logging
import sys
from colorama import Fore, Style, init

# Initialize colorama (for Windows compatibility)
init(autoreset=True)

# Define log colors
LOG_COLORS = {
    "DEBUG": Fore.CYAN,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.MAGENTA + Style.BRIGHT,
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors based on log levels."""

    def format(self, record):
        log_color = LOG_COLORS.get(record.levelname, Fore.WHITE)
        log_message = super().format(record)
        return f"{log_color}{log_message}{Style.RESET_ALL}"  # Reset color after log

# Set up logging
def get_logger(name: str):
    """Returns a logger with colored output."""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Prevent duplicate handlers
        handler = logging.StreamHandler(sys.stdout)
        formatter = ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
