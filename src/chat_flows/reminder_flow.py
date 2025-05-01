from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.chat_flows.chat_flow import ChatFlow
from src.logger import get_logger
from src.managers.prompt_manager import get_sakha_char_prompt
from src.response_templates.sakha_template import SakhaResponseForRemFlow
from src.utils import get_current_time_ist

logger = get_logger(__name__)


class ReminderFlow(ChatFlow):

    def generate_response(
        self,
        user_id, thread_id,
        exchange,
        user_input,
        latest_exchanges_pretty,
        user_info,
        conversation_summary="",
        activity_details=None,
    ):
        try:
            logger.info(
                f"Generating reminder response for activity: {activity_details}"
            )

            if exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(
                        f"Conversation History:\n{latest_exchanges_pretty}"
                    ),
                    SystemMessage(
                        f"Previously, you set a reminder for an activity for the user. It’s time! "
                        f"{activity_details}"
                        f"Encourage the user to start their activity with enthusiasm and motivation."
                    ),
                ]
            else:
                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(
                        f"Conversation History:\n{latest_exchanges_pretty}"
                    ),
                    SystemMessage(
                        f"{activity_details}. Motivate the user to complete the activity. "
                        f"If they seem reluctant, suggest small fun modifications to make it more enjoyable "
                        f"or provide alternatives. Otherwise, end the conversation."
                    ),
                    HumanMessage(user_input),
                ]

            model_response = self.llm.with_structured_output(
                SakhaResponseForRemFlow
            ).invoke(chat_prompt_msgs)
            logger.info("Successfully generated reminder response.")
            return model_response

        except Exception as e:
            logger.error(f"Error generating reminder response: {str(e)}", exc_info=True)
            return {
                "replyToUser": "Sorry, I ran into an issue. Can you try again?",
                "error": f"Error generating response in RemFlow",
            }
