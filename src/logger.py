import logging

# Configure logging once in a central place
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Create a logger instance
logger = logging.getLogger(__name__)
