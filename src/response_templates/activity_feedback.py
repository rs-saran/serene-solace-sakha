from typing import Optional

from pydantic import BaseModel, Field


class ActivityFeedback(BaseModel):
    """
    This data should only be recorded after explicit follow-up messages gather details about
    whether the user completed the activity, their enjoyment level if completed,
    or the reason for skipping if not completed.
    """

    activity_id: int = Field(description="The activity_id present in activity_details")
    completed: Optional[bool] = Field(
        None,
        description="Answers whether the user completed the activity (True) or skipped it (False). This should be determined through follow-up questions.",
    )
    enjoyment_score: Optional[int] = Field(
        None,
        description="A rating from 1 to 5 indicating how much the user enjoyed the activity. Should be collected only after confirming completion.",
    )
    reason_skipped: Optional[str] = Field(
        None,
        description="A short reason explaining why the user skipped the activity. Should be collected only after confirming the activity was not completed.",
    )
