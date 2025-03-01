from typing import Union
from pydantic import BaseModel
# from src.reminder import ReminderDatabase
from src.response_templates.activity_reminder_config import ActivityReminderConfig
from src.response_templates.supervisor_response import (
    FriennResponseForASFlow, FriennResponseForRemFlow, FriennResponseForFUFlow, ActivityFeedback
)
from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.reminder_manager import ReminderManager

class ResponseManager:
    """Handles chatbot responses and integrates with ReminderManager."""
    def __init__(self, reminder_manager: ReminderManager, db_manager: PostgresDBManager):
        self.reminder_manager = reminder_manager
        self.db_manager = db_manager

    def handle_response(self, response):
        """
        Handles different response flows based on the response type.
        """
        if isinstance(response, FriennResponseForASFlow):
            self._handle_as_flow(response)
        elif isinstance(response, FriennResponseForRemFlow):
            self._handle_rem_flow(response)
        elif isinstance(response, FriennResponseForFUFlow):
            self._handle_fu_flow(response)
        
        return response.replyToUser

    def _handle_as_flow(self, response):
        """
        Handles the Activity Suggestion Flow.
        Stores the reminder if all agreement conditions are met.
        """
        if response.didUserAgreeOnActivity and response.didUserAgreeOnTime and response.didUserAgreeOnDuration:
            if response.reminder:
                self.reminder_manager.add_reminder(
                    response.reminder.user_id,
                    response.reminder.activity,
                    response.reminder.start_time,
                    response.reminder.duration,
                    True, #response.reminder.send_reminder,
                    True, #response.reminder.send_followup
                )

    def _handle_fu_flow(self, response):
        """
        Handles the Follow-Up Flow.
        Stores feedback when feedback collection is complete.
        """
        if response.isFeedbackCollectionComplete and response.activityFeedback:
            query = """
            INSERT INTO activity_feedback (user_id, activity, feedback, rating) 
            VALUES (%s, %s, %s, %s)
            """
            self.db_manager.execute(query, (response.activityFeedback.user_id, response.activityFeedback.activity, response.activityFeedback.feedback, response.activityFeedback.rating))

    def _handle_rem_flow(self, response: FriennResponseForRemFlow):
        """
        Handles the Reminder Flow.
        Currently, it only determines whether to suggest alternatives.
        """
        pass  # No explicit database interaction needed for now

# Example Usage