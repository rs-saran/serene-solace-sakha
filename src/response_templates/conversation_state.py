from typing import List, TypedDict, Union

from langchain_core.messages import AnyMessage

from src.response_templates.sakha_template import (
    SakhaResponseForASFlow,
    SakhaResponseForError,
    SakhaResponseForFUFlow,
    SakhaResponseForNCFlow,
    SakhaResponseForRemFlow,
)
from src.response_templates.supervisor_response import SupervisorResponse
from src.response_templates.user_info import UserInfo
from src.response_templates.user_situation_gauger import SituationGaugerResponse


# Conversation State to hold all user interaction details
class ConversationState(TypedDict):
    user_id: str
    thread_id: str
    exchange: int
    reset_exchange: int

    reminder_start: bool
    followup_start: bool

    conversation_history: List[AnyMessage]
    preferred_activities: List[str]
    user_info: UserInfo
    user_input: str

    flow: str
    activity_details: dict
    to_user: str
    conversation_summary: str
    latest_exchanges: List[AnyMessage]

    latest_supervisor_response: SupervisorResponse
    latest_user_situation_gauger_response: SituationGaugerResponse

    latest_sakha_response: Union[
        SakhaResponseForNCFlow,
        SakhaResponseForASFlow,
        SakhaResponseForRemFlow,
        SakhaResponseForFUFlow,
        SakhaResponseForError,
    ]
    latest_nc_flow_response: SakhaResponseForNCFlow
    latest_as_flow_response: SakhaResponseForASFlow
    latest_rem_flow_response: SakhaResponseForRemFlow
    latest_fu_flow_response: SakhaResponseForFUFlow
