import psycopg
from psycopg_pool import ConnectionPool


class PostgresDBManager:
    """Manages database connections and setup."""

    _instance = None

    def __new__(
        cls,
        db_config={
            "dbname": "postgres",
            "user": "postgres",
            "password": "1234",
            "host": "localhost",
            "port": "5432",
        },
    ):
        if cls._instance is None:
            cls._instance = super(PostgresDBManager, cls).__new__(cls)
            cls._instance._initialize(db_config)
        return cls._instance

    def _initialize(self, db_config):
        CONNECTION_KWARGS = {
            "autocommit": True,
            "prepare_threshold": 0,
        }

        self.pool = ConnectionPool(
            conninfo=f"dbname={db_config['dbname']} user={db_config['user']} password={db_config['password']} host={db_config['host']} port={db_config['port']}",
            min_size=1,
            max_size=10,
            kwargs=CONNECTION_KWARGS,
        )
        self.setup()

    def setup(self):
        """Creates necessary tables if they do not exist."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                activity TEXT NOT NULL,
                hour INT NOT NULL,
                minute INT NOT NULL,
                duration INT NOT NULL,
                send_reminder BOOLEAN DEFAULT TRUE,
                send_followup BOOLEAN DEFAULT TRUE,
                is_reminder_sent BOOLEAN DEFAULT FALSE,
                is_followup_sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS activity_feedback (
                id SERIAL PRIMARY KEY,
                user_id TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                activity TEXT NOT NULL,
                is_completed BOOLEAN DEFAULT FALSE,
                enjoyment_score INT CHECK (enjoyment_score BETWEEN 1 AND 5),
                reason_skipped TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            self.execute(query)

        print("exceuted postgres setup")

    def execute(self, query, params=None, fetch=False):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                conn.commit()

    def close(self):
        self.pool.close()
