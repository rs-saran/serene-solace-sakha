import psycopg
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta

class ReminderManager:
    def __init__(self, db_config):
        self.db_config = db_config
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self._load_pending_reminders()

    def _get_db_connection(self):
        """Returns a new psycopg connection."""
        return psycopg.connect(**self.db_config)

    def _send_message(self, user_id, message):
        """Simulate sending a message to the user."""
        print(f"[{datetime.now()}] Sending to {user_id}: {message}")

    def _update_reminder_status(self, reminder_id, column):
        """Update reminder status in the database."""
        with self._get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"UPDATE reminders SET {column} = TRUE WHERE id = %s", (reminder_id,))
                conn.commit()

    def _schedule_reminder(self, reminder_id, user_id, activity, start_time, duration, send_reminder, send_followup):
        """Schedules reminders and follow-ups based on flags."""
        if send_reminder:
            self.scheduler.add_job(
                self._execute_reminder, 'date', run_date=start_time,
                args=[reminder_id, user_id, f"Reminder: Time for {activity}!"], id=f"reminder_{reminder_id}"
            )

        if send_followup:
            followup_time = start_time + timedelta(minutes=duration)
            self.scheduler.add_job(
                self._execute_followup, 'date', run_date=followup_time,
                args=[reminder_id, user_id, f"Follow-up: How was {activity}?"], id=f"followup_{reminder_id}"
            )

    def _execute_reminder(self, reminder_id, user_id, message):
        """Send reminder and update status in DB."""
        self._send_message(user_id, message)
        self._update_reminder_status(reminder_id, "is_reminder_sent")

    def _execute_followup(self, reminder_id, user_id, message):
        """Send follow-up and update status in DB."""
        self._send_message(user_id, message)
        self._update_reminder_status(reminder_id, "is_followup_sent")

    def _load_pending_reminders(self):
        """Load unsent reminders from the database on startup."""
        with self._get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, user_id, activity, start_time, duration, send_reminder, send_followup 
                    FROM reminders 
                    WHERE is_reminder_sent = FALSE OR is_followup_sent = FALSE
                """)
                rows = cursor.fetchall()

        for row in rows:
            reminder_id, user_id, activity, start_time, duration, send_reminder, send_followup = row
            self._schedule_reminder(reminder_id, user_id, activity, start_time, duration, send_reminder, send_followup)

    def add_reminder(self, user_id, activity, start_time, duration, send_reminder=True, send_followup=True):
        """Insert a new reminder into DB and schedule it."""
        with self._get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO reminders (user_id, activity, start_time, duration, send_reminder, send_followup) 
                    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
                    """,
                    (user_id, activity, start_time, duration, send_reminder, send_followup)
                )
                reminder_id = cursor.fetchone()[0]
                conn.commit()

        self._schedule_reminder(reminder_id, user_id, activity, start_time, duration, send_reminder, send_followup)
        print(f"Reminder for {activity} scheduled!")

# Example Usage
if __name__ == "__main__":
    DB_CONFIG = {
        "dbname": "your_db",
        "user": "your_user",
        "password": "your_password",
        "host": "localhost",
        "port": "5432",
    }

    reminder_manager = ReminderManager(DB_CONFIG)
    
    # Add test reminders
    start_time = datetime.now() + timedelta(seconds=10)  # 10 seconds later
    reminder_manager.add_reminder("user123", "Yoga", start_time, 5, send_reminder=True, send_followup=False)
    reminder_manager.add_reminder("user456", "Reading", start_time, 5, send_reminder=False, send_followup=True)
