from typing import TypedDict

from langchain_core.messages import AnyMessage

from src.response_templates.supervisor_response import SupervisorResponse
from src.response_templates.user_info import UserInfo


# Conversation State to hold all user interaction details
class ConversationState(TypedDict):
    user_id: str
    thread_id: str
    exchange: int
    reset_exchange: int
    conversation_history: list[AnyMessage]
    preferred_activities: list[str]
    user_info: UserInfo
    user_input: str
    supervisor_response: SupervisorResponse
    flow: str
    activity_details: dict
    to_user: str
    conversation_summary: str
    latest_exchanges: list[AnyMessage]
    reset_exchange: int
