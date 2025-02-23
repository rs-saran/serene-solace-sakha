from src.response_templates.frienn_template import FriennResponseForASFlow
from src.prompt_manager import get_activity_suggestion_prompt, get_frienn_char_prompt
from src.utils import get_current_time_ist
from src.chat_flows.chat_flow import ChatFlow
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage


class ActivitySuggestionFlow(ChatFlow):
    
    def generate_response(self, exchange, user_input, conversation_history_pretty, preferred_activities):
        if exchange == 0:
            chat_prompt_msgs = [
                SystemMessage(get_frienn_char_prompt()),
                SystemMessage(get_activity_suggestion_prompt()),
                SystemMessage("Introduce yourself briefly and naturally before suggesting an activity"),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                HumanMessage(user_input)
                    ]
        else: 
            chat_prompt_msgs = [
            SystemMessage(get_frienn_char_prompt()),
            SystemMessage(get_activity_suggestion_prompt()),
            SystemMessage(f"Activities preferred by user: {preferred_activities}"),
            SystemMessage(f"Current time: {get_current_time_ist()}"),
            SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
            HumanMessage(user_input)
                        ]
        
        model_response = self.llm.with_structured_output(FriennResponseForASFlow).invoke(chat_prompt_msgs)

        return model_response
