from langgraph.checkpoint.postgres import PostgresSaver
from psycopg_pool import ConnectionPool

class PostgresCheckpointerManager:
    """Handles PostgreSQL connection pooling and checkpointing."""

    DB_URI = "postgres://postgres:1234@localhost:5432/postgres?sslmode=disable"
    CONNECTION_KWARGS = {
        "autocommit": True,
        "prepare_threshold": 0,
    }

    def __init__(self):
        """Initialize the database connection pool and checkpointer."""
        self.pool = ConnectionPool(
            conninfo=self.DB_URI, max_size=20, kwargs=self.CONNECTION_KWARGS
        )
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


