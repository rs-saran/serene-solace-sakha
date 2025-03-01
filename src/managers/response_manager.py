from typing import Union
from pydantic import BaseModel
# from src.reminder import ReminderDatabase
from src.response_templates.activity_reminder_config import ActivityReminderConfig
from src.response_templates.supervisor_response import (
    FriennResponseForASFlow, FriennResponseForRemFlow, FriennResponseForFUFlow, ActivityFeedback
)

class ResponseManager:
    def __init__(self, reminder_db: ReminderDatabase, feedback_db):
        """
        Initializes the response manager.
        :param reminder_db: Database interface for storing reminders.
        :param feedback_db: Database interface for storing activity feedback.
        """
        self.reminder_db = reminder_db
        self.feedback_db = feedback_db

    def handle_response(self, response: Union[FriennResponseForASFlow, FriennResponseForRemFlow, FriennResponseForFUFlow]):
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

    def _handle_as_flow(self, response: FriennResponseForASFlow):
        """
        Handles the Activity Suggestion Flow.
        Stores the reminder if all agreement conditions are met.
        """
        if response.didUserAgreeOnActivity and response.didUserAgreeOnTime and response.didUserAgreeOnDuration:
            if response.reminder:
                self.reminder_db.store_reminder(response.reminder)

    def _handle_rem_flow(self, response: FriennResponseForRemFlow):
        """
        Handles the Reminder Flow.
        Currently, it only determines whether to suggest alternatives.
        """
        pass  # No explicit database interaction needed for now

    def _handle_fu_flow(self, response: FriennResponseForFUFlow):
        """
        Handles the Follow-Up Flow.
        Stores feedback when feedback collection is complete.
        """
        if response.isFeedbackCollectionComplete and response.activityFeedback:
            self.feedback_db.store_feedback(response.activityFeedback)

# Example usage:
# response_manager = ResponseManager(reminder_db=ReminderDatabase(), feedback_db=FeedbackDatabase())
# response_manager.handle_response(some_response)
