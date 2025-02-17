from pydantic import BaseModel, Field

class SupervisorResponse(BaseModel):
    "Route to proceed in"
    pickedRoute: str = Field(description= "The route to proceed in, ENUM: 'continue_chat', 'crisis_hepline'")
    reason: str =Field(description ="very short reason for picking the route")