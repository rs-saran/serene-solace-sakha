from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)

from src.chat_flows.chat_flow import ChatFlow
from src.managers.prompt_manager import (get_activity_suggestion_prompt,
                                         get_sakha_char_prompt)
from src.response_templates.sakha_template import SakhaResponseForRemFlow
from src.utils import get_current_time_ist


class ReminderFlow(ChatFlow):

    def generate_response(
        self, exchange, user_input, conversation_history_pretty, user_info, activity_details
    ):
        if exchange == 0:
            chat_prompt_msgs = [
                SystemMessage(get_sakha_char_prompt()),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(
                    f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"
                ),
                SystemMessage(
                    f"Previously you set a reminder for {activity_details}. It’s time! Encourage the user to start their activity with enthusiasm and motivation."
                ),
            ]
        else:
            chat_prompt_msgs = [
                SystemMessage(get_sakha_char_prompt()),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(
                    f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"
                ),
                SystemMessage(
                    f"Reminder details: {activity_details}. Motivate the user to complete the activity. If they seem reluctant, suggest small fun modifications to make it more enjoyable or alternatives else end the conversation."
                ),
                HumanMessage(user_input),
            ]

        model_response = self.llm.with_structured_output(
            SakhaResponseForRemFlow
        ).invoke(chat_prompt_msgs)

        return model_response
