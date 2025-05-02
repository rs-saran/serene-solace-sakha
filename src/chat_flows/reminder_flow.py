from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.chat_flows.chat_flow import ChatFlow
from src.logger import get_logger
from src.managers.prompt_manager import get_sakha_char_prompt
from src.response_templates.sakha_template import SakhaResponseForRemFlow
from src.utils import get_current_time_ist, exchanges_pretty

logger = get_logger(__name__)


class ReminderFlow(ChatFlow):

    def generate_response(
        self, conversation_state
    ):
        user_input = conversation_state.get("user_input")
        user_info = conversation_state.get("user_info", "no user_info")
        reminder_start = conversation_state.get("reminder_start", "no user_info")

        latest_exchanges = conversation_state.get("latest_exchanges", [])
        latest_exchanges_pretty = exchanges_pretty(latest_exchanges)
        conversation_summary = conversation_state.get("conversation_summary", "")
        activity_details = conversation_state.get("activity_details", "")

        try:
            logger.info(
                f"Generating reminder response for activity: {activity_details}"
            )
            chat_prompt_msgs = [
                SystemMessage(get_sakha_char_prompt()),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(f"User Info: {user_info}")]

            if conversation_summary == "":
                chat_context = f"Conversation History:\n{latest_exchanges_pretty}"
            else:
                chat_context = f"Conversation History:<conversation_history><summary>{conversation_summary}</summary> <latest_exchanges> {latest_exchanges_pretty} </latest_exchanges> </conversation_history>"

            chat_prompt_msgs.append(SystemMessage(chat_context))

            if reminder_start:
                reminder_instruction = f"Previously, you set a reminder for an activity for the user. It’s time!\n{activity_details}\nEncourage the user to start their activity with enthusiasm and motivation."
                chat_prompt_msgs.append(SystemMessage(reminder_instruction))
            else:
                reminder_instruction = f"{activity_details}. \n Motivate the user to complete the activity. If they seem reluctant, suggest small fun modifications to make it more enjoyable or ask if they want alternatives. Otherwise, end the conversation."
                chat_prompt_msgs.extend([SystemMessage(reminder_instruction), HumanMessage(user_input)])

            model_response = self.llm.with_structured_output(
                SakhaResponseForRemFlow
            ).invoke(chat_prompt_msgs)
            conversation_state.update(latest_sakha_response=model_response, latest_rem_flow_response=model_response, reminder_start=False)

            logger.info("Successfully generated reminder response.")

            return conversation_state

        except Exception as e:
            logger.error(f"Error generating reminder response: {str(e)}", exc_info=True)
            return conversation_state
