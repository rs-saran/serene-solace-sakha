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

    def _send_reminder(self, user_id: str, thread_id: str, activity_details: str):
        """Sends a reminder notification."""
        self._send_request(
            "send-reminder",
            {"user_id": user_id, "thread_id": thread_id, "activity_details": activity_details},
        )

    def _send_follow_up(self, user_id: str, thread_id: str, activity_details: str):
        """Sends a follow-up notification."""
        self._send_request(
            "send-follow-up",
            {"user_id": user_id, "thread_id": thread_id, "activity_details": activity_details},
        )

    def _update_activity_status(self, activity_id: int, column: str):
        """Marks a reminder as sent."""
        query = f"UPDATE activity_log SET {column} = TRUE WHERE id = %s"
        try:
            self.db_manager.execute(query, (activity_id,))
            logger.info(f"Reminder ID {activity_id}: {column} updated to TRUE.")
        except Exception as e:
            logger.error(f"Error updating reminder status: {e}", exc_info=True)

    def _schedule_reminder(
        self,
        activity_id: int,
        user_id: str,
        thread_id: str,
        user_situation: str,
        activity: str,
        hour: int,
        minute: int,
        duration: int,
        send_reminder: bool,
        send_followup: bool,
    ):
        """Schedules reminders and follow-ups."""
        ist = pytz.timezone("Asia/Kolkata")
        utc = pytz.utc  # APScheduler uses UTC
        now_ist = datetime.now(ist)

        start_time_ist = ist.localize(
            datetime(now_ist.year, now_ist.month, now_ist.day, hour, minute)
        )
        start_time_utc = start_time_ist.astimezone(utc)  # Convert IST to UTC

        logger.info(f"Scheduling Reminder: IST={start_time_ist}, UTC={start_time_utc}")

        activity_details = f"<activity_details>{{'activity_id': {activity_id}, 'user_situation': '{user_situation}', 'activity': '{activity}'}}</activity_details>"
        if send_reminder and start_time_ist > now_ist:
            self.scheduler.add_job(
                self._execute_reminder,
                "date",
                run_date=start_time_utc,
                args=[
                    activity_id,
                    user_id,
                    thread_id,
                    activity_details
                ],
                id=f"reminder_{activity_id}",
            )
            logger.info(f"Scheduled reminder for {activity} at {hour}:{minute} IST.")

        if send_followup:
            followup_time = start_time_utc + timedelta(minutes=duration)
            if followup_time > now_ist:
                self.scheduler.add_job(
                    self._execute_followup,
                    "date",
                    run_date=followup_time,
                    args=[
                        activity_id,
                        user_id,
                        thread_id,
                        activity_details,
                    ],
                    id=f"followup_{activity_id}",
                )
                logger.info(
                    f"Scheduled follow-up for {activity} at {followup_time.strftime('%H:%M')} IST."
                )

    def _execute_reminder(
        self, activity_id: int, user_id: str, thread_id: str, activity_details: str
    ):
        """Executes the reminder job."""
        self._send_reminder(user_id, thread_id, activity_details)
        self._update_activity_status(activity_id, "is_reminder_sent")

    def _execute_followup(
        self, activity_id: int, user_id: str, thread_id: str, activity_details: str
    ):
        """Executes the follow-up job."""
        self._send_follow_up(user_id, thread_id, activity_details)
        self._update_activity_status(activity_id, "is_followup_sent")

    def _load_pending_reminders(self):
        """Loads and schedules pending reminders from the database."""
        query = """
        SELECT id, user_id, thread_id, user_situation, activity, hour, minute, duration, send_reminder, send_followup
        FROM activity_log
        WHERE ((send_reminder = TRUE AND is_reminder_sent = FALSE)
        OR (send_followup = TRUE AND is_followup_sent = FALSE)) AND DATE(created_at) = CURRENT_DATE
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
        user_situation: str,
        activity: str,
        hour: int,
        minute: int,
        duration: int,
        send_reminder: bool = True,
        send_followup: bool = True,
    ) -> Optional[int]:
        """Adds a new reminder to the database and schedules it."""
        query = """
        INSERT INTO activity_log (user_id, thread_id, user_situation, activity, hour, minute, duration, send_reminder, send_followup)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
        """
        try:
            result = self.db_manager.execute(
                query,
                (
                    user_id,
                    thread_id,
                    user_situation,
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
                activity_id = result[0][0]
                self._schedule_reminder(
                    activity_id,
                    user_id,
                    thread_id,
                    user_situation,
                    activity,
                    hour,
                    minute,
                    duration,
                    send_reminder,
                    send_followup,
                )
                logger.info(f"Added reminder for {activity} at {hour}:{minute} IST.")
                return activity_id
        except Exception as e:
            logger.error(f"Error adding reminder: {e}", exc_info=True)

        return None

    def list_scheduled_jobs(self):
        """Returns a list of all scheduled jobs."""
        jobs = self.scheduler.get_jobs()
        job_list = []
        for job in jobs:
            job_list.append(
                {
                    "id": job.id,
                    "next_run_time": str(job.next_run_time),
                    "args": job.args,
                }
            )
        return job_list
