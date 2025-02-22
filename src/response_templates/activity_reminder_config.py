from pydantic import BaseModel, Field

class ActivityReminderConfig(BaseModel):

    """Activity Reminder to be set, updated, deleted or logged based on user agreement."""

    reminder_action: str = Field(description="ENUM: `set`: to set a reminder for later, `update`:to update the remider, `delete`:to delete the reminder, `log`:to log the activity details if immediate")
    activity: str = Field(description="The activity picked to improve user's mood.")
    hour: int = Field(description="Hour of Time at which activity should be done in 24 Hr format. Range: 0 to 23")
    minute: int = Field(description="Minute of Time at which activity should be done. Range: 0 to 59")
    duration: int = Field(description="Duration of activity in minutes")