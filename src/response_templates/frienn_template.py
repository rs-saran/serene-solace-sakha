from pydantic import BaseModel, Field
from typing import Union, Optional
from src.response_templates.activity_reminder_config import ActivityReminderConfig
from src.response_templates.activity_feedback import ActivityFeedback

class FriennResponseForASFlow(BaseModel):
    "Response template to follow"
    replyToUser: str = Field(description= "Reply to be shown to user")
    didUserAgreeOnActivity: bool = Field(description= "True if user agreed on actvity else False")
    didUserAgreeOnTime: bool = Field(description= "True if user agreed on time else False")
    didUserAgreeOnDuration: bool = Field(description= "True if user agreed on duration of the activity else False")
    reminder: Optional[ActivityReminderConfig] =Field(None, description ="set the reminder only when all [`didUserAgreeOnActivity`,`didUserAgreeOnTime`,`didUserAgreeOnDuration`] are TRUE.  Activity reminder tool call, help set, update or delete reminder.")


class FriennResponseForRemFlow(BaseModel):
    "Response template to follow"
    replyToUser: str = Field(description= "Reply to be shown to user")
    suggestAlternatives: bool = Field(description = "False if the user agrees and starts to do the activity")


class FriennResponseForFUFlow(BaseModel):
    "Response template to follow"
    replyToUser: str = Field(description= "Reply to be shown to user")
    isFeedbackCollectionComplete: bool = Field(description= "True if the feedback collection is complete")
    activityFeedback: Optional[ActivityFeedback] = Field(None, description ="Optional Activity Feedback info, fill it only after you collect the details from user")