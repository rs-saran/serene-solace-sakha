from typing import TypedDict, Literal
from langchain_core.messages import AnyMessage
from response_templates.supervisor_response import SupervisorResponse

# Conversation State to hold all user interaction details
class ConversationState(TypedDict):
    exchange: int
    conversation_history: list[AnyMessage]
    preferred_activities: list[str]
    user_input: str
    supervisor_response: SupervisorResponse
    flow: str
    