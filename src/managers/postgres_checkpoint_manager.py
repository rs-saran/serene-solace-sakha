from langgraph.checkpoint.postgres import PostgresSaver

from src.managers.postgres_db_manager import PostgresDBManager


class PostgresCheckpointerManager:
    """Handles PostgreSQL connection pooling and checkpointing."""

    def __init__(self, db_manager: PostgresDBManager):
        """Initialize the database connection pool and checkpointer."""
        self.pool = db_manager.pool
        self.checkpointer = PostgresSaver(self.pool)
        self._setup_database()

    def _setup_database(self):
        """Ensure the required tables exist in the PostgreSQL database."""
        self.checkpointer.setup()

    def get_checkpointer(self):
        """Return the checkpointer instance for use in the state graph."""
        return self.checkpointer

    def close(self):
        """Gracefully close the connection pool."""
        if self.pool:
            self.pool.close()
            print("PostgreSQL connection pool closed.")
