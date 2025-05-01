from src.logger import get_logger
from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.reminder_manager import ReminderManager
from src.response_templates.sakha_template import (
    SakhaResponseForNCFlow,
    SakhaResponseForASFlow,
    SakhaResponseForError,
    SakhaResponseForFUFlow,
    SakhaResponseForRemFlow,
)
from src.managers.memory_manager import MemoryManager

logger = get_logger(__name__)


class ResponseManager:
    """Handles chatbot responses and integrates with ReminderManager."""

    def __init__(
        self, reminder_manager: ReminderManager, db_manager: PostgresDBManager
    ):
        self.reminder_manager = reminder_manager
        self.db_manager = db_manager

    def _format_response(self, reply, activity_details=None):
        """Creates a standardized response format."""
        return {"reply": reply, "activity_details": activity_details}

    def handle_response(self, user_id, thread_id, response):
        """
        Handles different response flows based on the response type.
        """
        activity_details = None

        try:
            if isinstance(response, SakhaResponseForNCFlow):
                self._handle_nc_flow(user_id, thread_id, response)
            elif isinstance(response, SakhaResponseForASFlow):
                activity_details = self._handle_as_flow(user_id, thread_id, response)
            elif isinstance(response, SakhaResponseForRemFlow):
                self._handle_rem_flow(user_id, thread_id, response)
            elif isinstance(response, SakhaResponseForFUFlow):
                self._handle_fu_flow(user_id, thread_id, response)
            elif isinstance(response, SakhaResponseForError):
                self._handle_error_flow(user_id, thread_id, response)

            logger.info(
                f"Handled response type: {type(response).__name__} for user {user_id}."
            )
        except Exception as e:
            logger.error(
                f"Error handling response for user {user_id}: {e}", exc_info=True
            )

        return self._format_response(response.replyToUser, activity_details)

    def _handle_nc_flow(self, user_id, thread_id, response: SakhaResponseForASFlow):
        """
        Handles the response for Normal Chat Flow.
        """
        logger.info(f"Processing nc flow for user {user_id}, thread {thread_id}.")


    def _handle_as_flow(self, user_id, thread_id, response: SakhaResponseForASFlow):
        """
        Handles the Activity Suggestion Flow.
        Stores the reminder if all agreement conditions are met.
        """
        if (
            response.didUserAgreeOnActivity
            and response.didUserAgreeOnTime
            and response.didUserAgreeOnDuration
        ):
            if response.reminder:
                try:
                    self.reminder_manager.add_reminder(
                        user_id,
                        thread_id,
                        response.reminder.user_situation,
                        response.reminder.activity,
                        response.reminder.hour,
                        response.reminder.minute,
                        response.reminder.duration,
                        True,  # response.reminder.send_reminder
                        True,  # response.reminder.send_followup
                    )

                    activity_details = {
                        "user_situation": response.reminder.user_situation,
                        "activity": response.reminder.activity,
                        "time": f"{response.reminder.hour}:{response.reminder.minute}",
                        "duration": response.reminder.duration,
                    }

                    logger.info(
                        f"Reminder added: {activity_details} for user {user_id}."
                    )
                    return activity_details
                except Exception as e:
                    logger.error(
                        f"Error scheduling reminder for user {user_id}: {e}",
                        exc_info=True,
                    )

        return None

    def _handle_fu_flow(self, user_id, thread_id, response: SakhaResponseForFUFlow):
        """
        Handles the Follow-Up Flow.
        Stores feedback when feedback collection is complete.
        """
        if response.isFeedbackCollectionComplete and response.activityFeedback:
            # Storing feedback in postgres
            try:
                query = """
                        UPDATE activity_log
                        SET 
                            is_completed = %s,
                            enjoyment_score = %s,
                            reason_skipped = %s,
                            feedback_updated_at = CURRENT_TIMESTAMP
                        WHERE 
                            id = %s AND
                            user_id = %s AND
                            thread_id = %s
                        """
                self.db_manager.execute(
                    query,
                    (
                        response.activityFeedback.completed,
                        response.activityFeedback.enjoyment_score,
                        response.activityFeedback.reason_skipped,
                        response.activityFeedback.activity_id,
                        user_id,
                        thread_id,
                    ),
                )
                logger.info(
                    f"Feedback stored for user {user_id} on activity {response.activityFeedback.activity_id}."
                )
            except Exception as e:
                logger.error(
                    f"Error storing feedback for user {user_id}: {e}", exc_info=True
                )

            # Storing activity memory in qdrant
            try:
                query = """
                        SELECT  user_id, thread_id, id, user_situation, activity, duration, is_completed, enjoyment_score, reason_skipped, feedback_updated_at
                        FROM activity_log
                        WHERE id = %s AND
                            user_id = %s AND
                            thread_id = %s
                        """
                rows = self.db_manager.execute(
                    query,
                    (
                        response.activityFeedback.activity_id,
                        user_id,
                        thread_id,
                    ),
                    fetch=True
                )

                mem_manager = MemoryManager()

                if rows:
                    logger.info(
                        f"Found {len(rows)} activity memories. storing them now..."
                    )
                    for row in rows:
                        mem_manager.store_memory(*row)

                else:
                    logger.info("No activity memories. found.")

                logger.info(
                    f"Activity memories stored for user {user_id} on activity {response.activityFeedback.activity_id}."
                )
            except Exception as e:
                logger.error(
                    f"Error storing activity memories for user {user_id}: {e}", exc_info=True
                )



    def _handle_rem_flow(self, user_id, thread_id, response: SakhaResponseForRemFlow):
        """
        Handles the Reminder Flow.
        Currently, it only determines whether to suggest alternatives.
        """
        logger.info(f"Processing reminder flow for user {user_id}, thread {thread_id}.")

    def _handle_error_flow(self, user_id, thread_id, response: SakhaResponseForError):
        """
        Handles the Reminder Flow.
        Currently, it only determines whether to suggest alternatives.
        """
        logger.info(
            f"Processing error msg for user {user_id}, thread {thread_id}. \n {response.error}"
        )
