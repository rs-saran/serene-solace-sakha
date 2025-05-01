from pydantic import BaseModel, Field


class SupervisorResponse(BaseModel):
    """Route to proceed in"""

    pickedFlow: str = Field(
        description="The flow to proceed in, ENUM: 'normal_chat', 'crisis_helpline', 'reminder', 'follow_up', 'activity_suggestion'"
    )
    reason: str = Field(description="very shortly indicate the rule you followed for picking the flow")
