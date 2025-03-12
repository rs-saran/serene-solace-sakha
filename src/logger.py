import logging

# Configure logging once globally
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def get_logger(name: str):
    """Returns a logger with the given module name."""
    return logging.getLogger(name)
