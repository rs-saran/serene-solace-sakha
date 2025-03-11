from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)

from src.chat_flows.chat_flow import ChatFlow
from src.managers.prompt_manager import (get_activity_suggestion_prompt,
                                         get_frienn_char_prompt)
from src.response_templates.frienn_template import FriennResponseForFUFlow
from src.utils import get_current_time_ist, get_current_time_ist_30min_lag


class FollowUpFlow(ChatFlow):

    def generate_response(
        self, exchange, user_input, conversation_history_pretty, user_info
    ):
        if exchange == 0:
            chat_prompt_msgs = [
                SystemMessage(get_frienn_char_prompt()),
                SystemMessage(f"User Info: {user_info}"),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(
                    f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"
                ),
                SystemMessage(
                    f"You set a reminder for walking at {get_current_time_ist_30min_lag()}. Check in on the user’s experience—ask if they completed it and how it made them feel."
                ),
            ]
        else:
            chat_prompt_msgs = [
                SystemMessage(get_frienn_char_prompt()),
                SystemMessage(f"User Info: {user_info}"),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(
                    f"Previously you have set a reminder for walking at {get_current_time_ist_30min_lag()}. Now you are checking in on the user. Continue the conversation as friend and end the conversation. Do not suggest more activities if user is feeling"
                ),
                SystemMessage(
                    f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"
                ),
                HumanMessage(user_input),
            ]

        model_response = self.llm.with_structured_output(
            FriennResponseForFUFlow
        ).invoke(chat_prompt_msgs)

        return model_response
