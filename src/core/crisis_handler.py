from src.logger import get_logger

logger = get_logger(__name__)


def crisis_handler(state):
    """Handles crisis situations by providing an emergency helpline with logging."""
    try:
        logger.info("CrisisHandler invoked.")
        message = (
            "You seem to be in an active crisis. Please call 1800-599-0019, a 24/7 toll-free helpline "
            "launched by the Ministry of Social Justice and Empowerment of India."
        )
        return {"to_user": message}
    except Exception as e:
        logger.error(f"Error in CrisisHandler: {str(e)}", exc_info=True)
        return "An error occurred while processing your request. If you are in crisis, please seek immediate help."
