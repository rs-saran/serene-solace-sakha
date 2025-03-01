import psycopg
from psycopg_pool import ConnectionPool

class PostgresDBManager:
    _instance = None  # Singleton instance

    def __new__(cls, db_config):
        if cls._instance is None:
            cls._instance = super(PostgresDBManager, cls).__new__(cls)
            cls._instance._initialize(db_config)
        return cls._instance

    def _initialize(self, db_config):
        self.pool = ConnectionPool(
            conninfo=f"dbname={db_config['dbname']} user={db_config['user']} password={db_config['password']} host={db_config['host']} port={db_config['port']}",
            min_size=1,
            max_size=10
        )
        self.setup()  # Ensure tables exist

    def setup(self):
        """Creates necessary tables if they do not exist."""
        create_reminder_table = """
        CREATE TABLE IF NOT EXISTS reminder (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            activity TEXT NOT NULL,
            reminder_time TIMESTAMP NOT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_activity_feedback_table = """
        CREATE TABLE IF NOT EXISTS activity_feedback (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            activity TEXT NOT NULL,
            feedback TEXT,
            rating INT CHECK (rating BETWEEN 1 AND 5),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        create_user_preferences_table = """
        CREATE TABLE IF NOT EXISTS user_preferences (
            user_id INT NOT NULL,
            preferred_activities TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        self.execute(create_reminder_table)
        self.execute(create_activity_feedback_table)

    def store_reminder(self, user_id, activity, reminder_time, status="pending"):
        """Inserts a new reminder into the database."""
        query = """
        INSERT INTO reminder (user_id, activity, reminder_time, status)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """
        return self.execute(query, (user_id, activity, reminder_time, status), fetch=True)

    def store_activity_feedback(self, user_id, activity, feedback, rating):
        """Inserts activity feedback into the database."""
        query = """
        INSERT INTO activity_feedback (user_id, activity, feedback, rating)
        VALUES (%s, %s, %s, %s) RETURNING id;
        """
        return self.execute(query, (user_id, activity, feedback, rating), fetch=True)

    def execute(self, query, params=None, fetch=False):
        with self.pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
                conn.commit()

    def close(self):
        self.pool.close()

# Usage:
# db_config = {
#     "user": "postgres",
#     "password": "password",
#     "host": "localhost",
#     "port": "5432",
#     "dbname": "frienn_db"
# }

# db_manager = PostgresDBManager(db_config)

# # Insert example data
# reminder_id = db_manager.insert_reminder(1, "Go for a walk", "2025-02-26 10:00:00")
# print(f"Inserted Reminder ID: {reminder_id}")

# feedback_id = db_manager.insert_activity_feedback(1, "Go for a walk", "It was refreshing!", 5)
# print(f"Inserted Feedback ID: {feedback_id}")
