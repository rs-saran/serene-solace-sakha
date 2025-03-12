
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from src.chat_flows.chat_flow import ChatFlow
from src.managers.prompt_manager import get_activity_suggestion_prompt, get_sakha_char_prompt
from src.response_templates.sakha_template import SakhaResponseForFUFlow
from src.utils import get_current_time_ist
from src.logger import logger

class FollowUpFlow(ChatFlow):

    def generate_response(self, exchange, user_input, conversation_history_pretty, user_info, activity_details):
        try:
            logger.info(f"Generating follow-up response for user_input: {user_input}")

            if exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(f"User Info: {user_info}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Conversation History:\n{conversation_history_pretty}"),
                    SystemMessage(
                        f"Previously, you suggested an activity to the user. "
                        f"Activity details: {activity_details}. Check in on the user’s experience—"
                        f"ask if they completed it and how it made them feel."
                    ),
                ]
            else:
                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(f"User Info: {user_info}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(
                        f"Previously, you suggested an activity to the user. "
                        f"Activity details: {activity_details}. Now you are following up with the user. "
                        f"Continue the conversation as a friend, collect feedback, and end the conversation "
                        f"after feedback is collected. Do not suggest more activities if the user is feeling fine."
                    ),
                    SystemMessage(f"Conversation History:\n{conversation_history_pretty}"),
                    HumanMessage(user_input),
                ]

            model_response = self.llm.with_structured_output(SakhaResponseForFUFlow).invoke(chat_prompt_msgs)
            logger.info("Successfully generated follow-up response.")
            return model_response

        except Exception as e:
            logger.error(f"Error generating follow-up response: {str(e)}", exc_info=True)
            return {"error": "Sorry, I ran into an issue. Can you try again?"}
