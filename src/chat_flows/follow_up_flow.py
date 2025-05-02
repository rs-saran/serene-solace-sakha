from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.chat_flows.chat_flow import ChatFlow
from src.logger import get_logger
from src.managers.prompt_manager import (
    get_activity_suggestion_prompt,
    get_sakha_char_prompt,
)
from src.response_templates.sakha_template import SakhaResponseForFUFlow
from src.utils import get_current_time_ist, exchanges_pretty

logger = get_logger(__name__)


class FollowUpFlow(ChatFlow):

    def generate_response(
        self, conversation_state
    ):
        user_input = conversation_state.get("user_input")
        user_info = conversation_state.get("user_info", "no user_info")
        followup_start = conversation_state.get("followup_start", "no user_info")

        latest_exchanges = conversation_state.get("latest_exchanges", [])
        latest_exchanges_pretty = exchanges_pretty(latest_exchanges)
        conversation_summary = conversation_state.get("conversation_summary", "")
        activity_details = conversation_state.get("activity_details", "")

        try:
            logger.info(f"Generating follow-up response for user_input: {user_input}")

            chat_prompt_msgs = [
                SystemMessage(get_sakha_char_prompt()),
                SystemMessage(f"User Info: {user_info}"),
                SystemMessage(f"Current time: {get_current_time_ist()}")]

            if followup_start:
                chat_context = f"Conversation Summary:<summary>{conversation_summary}</summary>"
            elif conversation_summary == "":
                chat_context = f"Conversation History:\n{latest_exchanges_pretty}"
            else:
                chat_context = f"Conversation History:<conversation_history><summary>{conversation_summary}</summary> <latest_exchanges> {latest_exchanges_pretty} </latest_exchanges> </conversation_history>"

            chat_prompt_msgs.append(SystemMessage(chat_context))

            if followup_start:
                chat_prompt_msgs.append(SystemMessage(
                    f"Previously, you suggested an activity to the user. "
                    f"{activity_details}. Check in on the user’s experience."
                    f"ask if they completed it and how it made them feel."
                ))
            else:
                chat_prompt_msgs.append(SystemMessage(
                        f"Previously, you suggested an activity to the user. Now you are following up with the user. "
                        f"{activity_details}"
                        f"Continue the conversation as a friend, collect feedback, and end the conversation "
                        f"after feedback is collected. Do not suggest more activities if the user is feeling fine."
                    ))
                chat_prompt_msgs.append(HumanMessage(user_input))

            model_response = self.llm.with_structured_output(
                SakhaResponseForFUFlow
            ).invoke(chat_prompt_msgs)
            logger.info("Successfully generated follow-up response.")
            conversation_state.update(latest_sakha_response=model_response, latest_rem_flow_response=model_response,
                                      followup_start=False)

            return conversation_state

        except Exception as e:
            logger.error(
                f"Error generating follow-up response: {str(e)}", exc_info=True
            )
            return conversation_state
