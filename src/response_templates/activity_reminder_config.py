from pydantic import BaseModel, Field

class ActivityReminderConfig(BaseModel):
    "Ativity Reminder config"
    activity: str = Field(description="The activity picked to improve user's mood")
    hour: int = Field(description="Hour of Time at which activity should be done in 24 Hr format. Range: 0 to 23")
    minute: int = Field(description="Minute of Time at which activity should be done. Range: 0 to 59")