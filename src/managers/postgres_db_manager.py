import psycopg
from psycopg_pool import ConnectionPool

from src.logger import get_logger

logger = get_logger(__name__)


class PostgresDBManager:
    """Manages database connections and setup using a connection pool."""

    _instance = None

    def __new__(
        cls,
        db_config=None,
    ):
        if db_config is None:
            raise ValueError("db_config is required for postgres_db_manager")
        if any(value is None for value in db_config.values()):
            raise ValueError("All values in db_config are required for postgres_db_manager")
        if cls._instance is None:
            cls._instance = super(PostgresDBManager, cls).__new__(cls)
            try:
                cls._instance._initialize(db_config)
                logger.info("Database connection pool initialized successfully.")
            except Exception as e:
                logger.exception("Failed to initialize database connection pool.")
                raise e  # Prevent execution if DB setup fails
        return cls._instance

    def _initialize(self, db_config):
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }

        try:
            self.pool = ConnectionPool(
                conninfo=f"dbname={db_config['dbname']} user={db_config['user']} password={db_config['password']} host={db_config['host']} port={db_config['port']}",
                min_size=1,
                max_size=10,
                kwargs=connection_kwargs,
            )
            self.setup()
        except Exception as e:
            logger.exception("Error initializing the database pool.")
            raise

    def setup(self):
        """Creates necessary tables if they do not exist."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS activity_log (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_situation TEXT NOT NULL,
                activity TEXT NOT NULL,
                hour INT NOT NULL,
                minute INT NOT NULL,
                duration INT NOT NULL,
                send_reminder BOOLEAN DEFAULT TRUE,
                send_followup BOOLEAN DEFAULT TRUE,
                is_reminder_sent BOOLEAN DEFAULT FALSE,
                is_followup_sent BOOLEAN DEFAULT FALSE,
                
                is_completed BOOLEAN DEFAULT FALSE,
                enjoyment_score INT DEFAULT NULL  CHECK ((enjoyment_score BETWEEN 1 AND 5) OR enjoyment_score is null),
                reason_skipped TEXT DEFAULT NULL,
                feedback_updated_at TIMESTAMP DEFAULT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                session_count INT DEFAULT 0,
                name VARCHAR(100) NOT NULL,
                age_range VARCHAR(20),
                preferred_activities TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
        ]
        for query in queries:
            try:
                self.execute(query)
                logger.info("Successfully executed setup query.")
            except Exception as e:
                logger.exception("Error executing setup query.")

    def execute(self, query, params=None, fetch=False):
        """Executes SQL queries with error handling."""
        try:
            with self.pool.connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    if fetch:
                        result = cur.fetchall()
                        logger.info(f"Query executed successfully: {query}")
                        return result
                    conn.commit()
                    logger.info(f"Query executed and committed successfully.")
        except psycopg.DatabaseError as e:
            logger.exception(f"Database error executing query: {query}")
            return None  # Handle failure gracefully
        except Exception as e:
            logger.exception(f"Unexpected error executing query: {query}")
            return None

    def close(self):
        """Closes the database connection pool."""
        try:
            self.pool.close()
            logger.info("Database connection pool closed successfully.")
        except Exception as e:
            logger.exception("Error closing the database connection pool.")
