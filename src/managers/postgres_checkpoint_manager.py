import logging
from langgraph.checkpoint.postgres import PostgresSaver
from src.managers.postgres_db_manager import PostgresDBManager

# Set up logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class PostgresCheckpointerManager:
    """Handles PostgreSQL connection pooling and checkpointing."""

    def __init__(self, db_manager: PostgresDBManager):
        """Initialize the database connection pool and checkpointer."""
        self.pool = db_manager.pool
        try:
            self.checkpointer = PostgresSaver(self.pool)
            self._setup_database()
            logger.info("PostgreSQL checkpointer initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize PostgreSQL checkpointer.")

    def _setup_database(self):
        """Ensure the required tables exist in the PostgreSQL database."""
        try:
            self.checkpointer.setup()
            logger.info("Checkpointing table setup completed.")
        except Exception as e:
            logger.exception("Error setting up checkpointing table.")

    def get_checkpointer(self):
        """Return the checkpointer instance for use in the state graph."""
        return self.checkpointer

    def close(self):
        """Gracefully close the connection pool."""
        if self.pool:
            try:
                self.pool.close()
                logger.info("PostgreSQL connection pool closed successfully.")
            except Exception as e:
                logger.exception("Error while closing PostgreSQL connection pool.")
