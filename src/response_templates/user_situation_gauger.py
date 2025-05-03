from typing import Optional

from pydantic import BaseModel, Field


class SituationGaugerResponse(BaseModel):
    """Response template to follow"""

    userSituation: str = Field(
        description="A brief but specific description of the user's emotional or situational context (e.g., 'feeling anxious before a meeting', 'low energy in the afternoon', or 'excitied about a new project')"
    )
