from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage)
from src.chat_flows.chat_flow import ChatFlow
from src.managers.prompt_manager import (get_activity_suggestion_prompt, get_sakha_char_prompt)
from src.response_templates.sakha_template import SakhaResponseForASFlow
from src.utils import get_current_time_ist

from src.logger import get_logger

logger = get_logger(__name__)


class ActivitySuggestionFlow(ChatFlow):
    
    def generate_response(
        self, exchange, user_input, conversation_history_pretty, user_info, activity_details=None
    ):
        try:
            logger.info(f"Generating response for user_input in Activity suggestion flow : {user_input}")
            
            if exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(f"User Info: {user_info}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage("Introduce yourself briefly and naturally and check how the user is doing."),
                    HumanMessage(user_input),
                ]
            else:
                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(get_activity_suggestion_prompt()),
                    SystemMessage(f"User Info: {user_info}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                    HumanMessage(user_input),
                ]

            model_response = self.llm.with_structured_output(SakhaResponseForASFlow).invoke(chat_prompt_msgs)
            
            logger.info("Successfully generated response in AS Flow")
            return model_response
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return {"error": "Sorry, I ran into an issue. Can you try again?"}
