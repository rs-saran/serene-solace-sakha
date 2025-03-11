from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from src.managers.postgres_db_manager import PostgresDBManager

import requests


class ReminderManager:
    """Handles storing and scheduling reminders."""

    def __init__(self, db_manager: PostgresDBManager):
        self.db_manager = db_manager
        # self.scheduler = BackgroundScheduler()
        # self.scheduler.start()
        # self._load_pending_reminders()

    def _send_message(self, user_id, message):
        print(f"[{datetime.now()}] Sending to {user_id}: {message}")

    def _update_reminder_status(self, reminder_id, column):
        query = f"UPDATE reminders SET {column} = TRUE WHERE id = %s"
        self.db_manager.execute(query, (reminder_id,))

    def _schedule_reminder(
        self,
        reminder_id,
        user_id,
        activity,
        hour,
        minute,
        duration,
        send_reminder,
        send_followup,
    ):
        if send_reminder:
            self.scheduler.add_job(
                self._execute_reminder,
                "date",
                run_date=start_time,
                args=[reminder_id, user_id, f"Reminder: Time for {activity}!"],
                id=f"reminder_{reminder_id}",
            )

        if send_followup:
            followup_time = start_time + timedelta(minutes=duration)
            self.scheduler.add_job(
                self._execute_followup,
                "date",
                run_date=followup_time,
                args=[reminder_id, user_id, f"Follow-up: How was {activity}?"],
                id=f"followup_{reminder_id}",
            )

    def _execute_reminder(self, reminder_id, user_id, message):
        self._send_message(user_id, message)
        self._update_reminder_status(reminder_id, "is_reminder_sent")

    def _execute_followup(self, reminder_id, user_id, message):
        self._send_message(user_id, message)
        self._update_reminder_status(reminder_id, "is_followup_sent")

    def _load_pending_reminders(self):
        query = """
        SELECT id, user_id, activity, hour, minute, duration, send_reminder, send_followup 
        FROM reminders 
        WHERE is_reminder_sent = FALSE OR is_followup_sent = FALSE
        """
        rows = self.db_manager.execute(query, fetch=True)
        for row in rows:
            self._schedule_reminder(*row)

    def add_reminder(
        self,
        user_id,
        thread_id, 
        activity,
        hour,
        minute,
        duration,
        send_reminder=True,
        send_followup=True,
    ):
        query = """
        INSERT INTO reminders (user_id, thread_id, activity, hour, minute, duration, send_reminder, send_followup) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        reminder_id = self.db_manager.execute(
            query,
            (user_id, thread_id, activity, hour, minute, duration, send_reminder, send_followup),
            fetch=True,
        )[0][0]
        # self._schedule_reminder(reminder_id, user_id, activity, start_time, duration, send_reminder, send_followup)
        print(f"Reminder for {activity} at {hour}:{minute} for {duration} mins is scheduled!")
