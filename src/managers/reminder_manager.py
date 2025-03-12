from datetime import datetime, timedelta
from typing import Optional

import pytz
import requests
from apscheduler.schedulers.background import BackgroundScheduler

from src.logger import get_logger
from src.managers.postgres_db_manager import PostgresDBManager

logger = get_logger(__name__)


class ReminderManager:
    """Handles storing and scheduling reminders."""

    def __init__(self, db_manager: PostgresDBManager, base_url: str):
        self.db_manager = db_manager
        self.BASE_URL = base_url
        self.scheduler = BackgroundScheduler(daemon=True)
        self.scheduler.start()
        self._load_pending_reminders()

    def _send_request(self, endpoint: str, data: dict):
        """Helper function to send HTTP requests."""
        try:
            response = requests.post(f"{self.BASE_URL}/{endpoint}/", json=data)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error sending request to {endpoint}: {e}", exc_info=True)
            return None

    def _send_reminder(self, user_id: str, thread_id: str, message: str):
        """Sends a reminder notification."""
        self._send_request(
            "send-reminder",
            {"user_id": user_id, "thread_id": thread_id, "message": message},
        )

    def _send_follow_up(self, user_id: str, thread_id: str, message: str):
        """Sends a follow-up notification."""
        self._send_request(
            "follow-up",
            {"user_id": user_id, "thread_id": thread_id, "message": message},
        )

    def _update_reminder_status(self, reminder_id: int, column: str):
        """Marks a reminder as sent."""
        query = f"UPDATE reminders SET {column} = TRUE WHERE id = %s"
        try:
            self.db_manager.execute(query, (reminder_id,))
            logger.info(f"Reminder ID {reminder_id}: {column} updated to TRUE.")
        except Exception as e:
            logger.error(f"Error updating reminder status: {e}", exc_info=True)

    def _schedule_reminder(
        self,
        reminder_id: int,
        user_id: str,
        thread_id: str,
        activity: str,
        hour: int,
        minute: int,
        duration: int,
        send_reminder: bool,
        send_followup: bool,
    ):
        """Schedules reminders and follow-ups."""
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist)
        start_time = datetime(
            now_ist.year, now_ist.month, now_ist.day, hour, minute, tzinfo=ist
        )

        if send_reminder and start_time > now_ist:
            self.scheduler.add_job(
                self._execute_reminder,
                "date",
                run_date=start_time,
                args=[
                    reminder_id,
                    user_id,
                    thread_id,
                    f"Reminder: Time for {activity}!",
                ],
                id=f"reminder_{reminder_id}",
            )
            logger.info(f"Scheduled reminder for {activity} at {hour}:{minute} IST.")

        if send_followup:
            followup_time = start_time + timedelta(minutes=duration)
            if followup_time > now_ist:
                self.scheduler.add_job(
                    self._execute_followup,
                    "date",
                    run_date=followup_time,
                    args=[
                        reminder_id,
                        user_id,
                        thread_id,
                        f"Follow-up: How was {activity}?",
                    ],
                    id=f"followup_{reminder_id}",
                )
                logger.info(
                    f"Scheduled follow-up for {activity} at {followup_time.strftime('%H:%M')} IST."
                )

    def _execute_reminder(
        self, reminder_id: int, user_id: str, thread_id: str, message: str
    ):
        """Executes the reminder job."""
        self._send_reminder(user_id, thread_id, message)
        self._update_reminder_status(reminder_id, "is_reminder_sent")

    def _execute_followup(
        self, reminder_id: int, user_id: str, thread_id: str, message: str
    ):
        """Executes the follow-up job."""
        self._send_follow_up(user_id, thread_id, message)
        self._update_reminder_status(reminder_id, "is_followup_sent")

    def _load_pending_reminders(self):
        """Loads and schedules pending reminders from the database."""
        query = """
        SELECT id, user_id, thread_id, activity, hour, minute, duration, send_reminder, send_followup
        FROM reminders
        WHERE (send_reminder = TRUE AND is_reminder_sent = FALSE)
        OR (send_followup = TRUE AND is_followup_sent = FALSE)
        """
        try:
            rows = self.db_manager.execute(query, fetch=True)
            if rows:
                logger.info(
                    f"Found {len(rows)} pending reminders. Scheduling them now..."
                )
                for row in rows:
                    self._schedule_reminder(*row)
            else:
                logger.info("No pending reminders found.")
        except Exception as e:
            logger.error(f"Error loading pending reminders: {e}", exc_info=True)

    def add_reminder(
        self,
        user_id: str,
        thread_id: str,
        activity: str,
        hour: int,
        minute: int,
        duration: int,
        send_reminder: bool = True,
        send_followup: bool = True,
    ) -> Optional[int]:
        """Adds a new reminder to the database and schedules it."""
        query = """
        INSERT INTO reminders (user_id, thread_id, activity, hour, minute, duration, send_reminder, send_followup)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        try:
            result = self.db_manager.execute(
                query,
                (
                    user_id,
                    thread_id,
                    activity,
                    hour,
                    minute,
                    duration,
                    send_reminder,
                    send_followup,
                ),
                fetch=True,
            )
            if result:
                reminder_id = result[0][0]
                self._schedule_reminder(
                    reminder_id,
                    user_id,
                    thread_id,
                    activity,
                    hour,
                    minute,
                    duration,
                    send_reminder,
                    send_followup,
                )
                logger.info(f"Added reminder for {activity} at {hour}:{minute} IST.")
                return reminder_id
        except Exception as e:
            logger.error(f"Error adding reminder: {e}", exc_info=True)

        return None
