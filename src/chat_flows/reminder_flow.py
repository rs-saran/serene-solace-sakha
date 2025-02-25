from src.response_templates.frienn_template import FriennResponseForRemFlow
from src.managers.prompt_manager import get_activity_suggestion_prompt, get_frienn_char_prompt
from src.chat_flows.chat_flow import ChatFlow
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from src.utils import get_current_time_ist



class ReminderFlow(ChatFlow):

    def get_reminder_details(self):
        return f"walking at {get_current_time_ist()}"
    
    def generate_response(self, exchange, user_input, conversation_history_pretty, preferred_activities):
        if exchange == 0:
            chat_prompt_msgs = [
                SystemMessage(get_frienn_char_prompt()),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                SystemMessage(f"Previously you set a reminder for {self.get_reminder_details()}. It’s time! Encourage the user to start their activity with enthusiasm and motivation."),
            ]
        else:
            chat_prompt_msgs = [
                SystemMessage(get_frienn_char_prompt()),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                SystemMessage(f"Reminder details: {self.get_reminder_details()}. Motivate the user to complete the activity. If they seem reluctant, suggest small fun modifications to make it more enjoyable or alternatives else end the conversation."),
                HumanMessage(user_input)
            ]

        model_response = self.llm.with_structured_output(FriennResponseForRemFlow).invoke(chat_prompt_msgs)

        return model_response
