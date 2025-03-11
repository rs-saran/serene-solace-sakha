from typing import Union

from pydantic import BaseModel

from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.reminder_manager import ReminderManager
from src.response_templates.activity_reminder_config import \
    ActivityReminderConfig
from src.response_templates.activity_feedback import ActivityFeedback
from src.response_templates.sakha_template import (SakhaResponseForASFlow,
                                                    SakhaResponseForFUFlow,
                                                    SakhaResponseForRemFlow)


class ResponseManager:
    """Handles chatbot responses and integrates with ReminderManager."""

    def __init__(
        self, reminder_manager: ReminderManager, db_manager: PostgresDBManager
    ):
        self.reminder_manager = reminder_manager
        self.db_manager = db_manager

    def _format_response(self, reply, activity_details=None):
        """Helper function to create a standardized response format."""
        return {"reply": reply, "activity_details": activity_details}

    def handle_response(self, user_id, thread_id, response):
        """
        Handles different response flows based on the response type.
        """
        activity_details = None

        if isinstance(response, SakhaResponseForASFlow):
            activity_details = self._handle_as_flow(user_id, thread_id, response)
        elif isinstance(response, SakhaResponseForRemFlow):
            self._handle_rem_flow(user_id, thread_id, response)
        elif isinstance(response, SakhaResponseForFUFlow):
            self._handle_fu_flow(user_id, thread_id, response)

        return self._format_response(response.replyToUser, activity_details)

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
                self.reminder_manager.add_reminder(
                    user_id,
                    thread_id, 
                    response.reminder.activity,
                    response.reminder.hour,
                    response.reminder.minute,
                    response.reminder.duration,
                    True,  # response.reminder.send_reminder,
                    True,  # response.reminder.send_followup
                )

                activity_details = {'activity':response.reminder.activity, 'time': f'{response.reminder.hour}:{response.reminder.minute}', 'duration': response.reminder.duration}

                return activity_details
        
        return None

    def _handle_fu_flow(self, user_id, thread_id, response: SakhaResponseForRemFlow):
        """
        Handles the Follow-Up Flow.
        Stores feedback when feedback collection is complete.
        """
        if response.isFeedbackCollectionComplete and response.activityFeedback:
            query = """
            INSERT INTO activity_feedback (user_id, thread_id, activity, is_completed, enjoyment_score, reason_skipped) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            self.db_manager.execute(
                query,
                (
                    user_id,
                    thread_id, 
                    response.activityFeedback.activity,
                    response.activityFeedback.is_completed,
                    response.activityFeedback.enjoyment_score,
                    response.activityFeedback.reason_skipped,
                ),
            )


    def _handle_rem_flow(self, user_id, thread_id, response: SakhaResponseForRemFlow):
        """
        Handles the Reminder Flow.
        Currently, it only determines whether to suggest alternatives.
        """
        pass  # No explicit database interaction needed for now


# Example Usage
