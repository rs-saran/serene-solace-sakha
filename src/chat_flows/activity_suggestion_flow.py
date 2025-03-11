from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)

from src.chat_flows.chat_flow import ChatFlow
from src.managers.prompt_manager import (get_activity_suggestion_prompt,
                                         get_frienn_char_prompt)
from src.response_templates.frienn_template import FriennResponseForASFlow
from src.utils import get_current_time_ist


class ActivitySuggestionFlow(ChatFlow):

    def generate_response(
        self, exchange, user_input, conversation_history_pretty, user_info
    ):
        if exchange == 0:
            chat_prompt_msgs = [
                SystemMessage(get_frienn_char_prompt()),
                SystemMessage(f"User Info: {user_info}"),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(
                    "Introduce yourself briefly and naturally and check how the user is doing."
                ),
                HumanMessage(user_input),
            ]
        else:
            chat_prompt_msgs = [
                SystemMessage(get_frienn_char_prompt()),
                SystemMessage(get_activity_suggestion_prompt()),
                SystemMessage(f"User Info: {user_info}"),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(
                    f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"
                ),
                HumanMessage(user_input),
            ]

        model_response = self.llm.with_structured_output(
            FriennResponseForASFlow
        ).invoke(chat_prompt_msgs)

        return model_response
