from pydantic import BaseModel, Field


class ActivityReminderConfig(BaseModel):
    """Activity Reminder to be set, updated, deleted"""

    reminder_action: str = Field(
        description="ENUM: `set`: to set a reminder for later, `update`:to update the reminder if one is already set, `delete`:to delete the reminder"
    )
    user_situation: str = Field(
        description="A brief but specific description of the user's emotional or situational context when the activity is suggested (e.g., 'feeling anxious before a meeting', 'low energy in the afternoon', or 'winding down after a stressful day')"
    )
    activity: str = Field(description="The activity picked to improve user's mood.")
    hour: int = Field(
        description="Hour of Time at which activity should be done in 24 Hr format. Range: 0 to 23"
    )
    minute: int = Field(
        description="Minute of Time at which activity should be done. Range: 0 to 59"
    )
    duration: int = Field(description="Duration of activity in minutes")
