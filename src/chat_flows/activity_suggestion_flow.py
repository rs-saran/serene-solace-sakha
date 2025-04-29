from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.callbacks import UsageMetadataCallbackHandler

from src.chat_flows.chat_flow import ChatFlow
from src.logger import get_logger
from src.managers.prompt_manager import (
    get_activity_suggestion_prompt,
    get_sakha_char_prompt,
)
from src.response_templates.sakha_template import SakhaResponseForASFlow
from src.utils import get_current_time_ist

logger = get_logger(__name__)


class ActivitySuggestionFlow(ChatFlow):

    def generate_response(
        self,
        exchange,
        user_input,
        latest_exchanges_pretty,
        user_info,
        conversation_summary="",
        activity_details=None,
    ):
        try:
            logger.info(
                f"Generating response for user_input in Activity suggestion flow : {user_input}"
            )

            if exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(f"User Info: {user_info}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(
                        "Suggest some activity to the user"
                    ),
                    HumanMessage(user_input),
                ]
            else:
                if conversation_summary == "":
                    chat_prompt_msgs = [
                        SystemMessage(get_sakha_char_prompt()),
                        SystemMessage(get_activity_suggestion_prompt()),
                        SystemMessage(f"User Info: {user_info}"),
                        SystemMessage(f"Current time: {get_current_time_ist()}"),
                        SystemMessage(
                            f"Conversation History:<conversation_history>{latest_exchanges_pretty}</conversation_history>"
                        ),
                        HumanMessage(user_input),
                    ]
                else:
                    chat_prompt_msgs = [
                        SystemMessage(get_sakha_char_prompt()),
                        SystemMessage(get_activity_suggestion_prompt()),
                        SystemMessage(f"User Info: {user_info}"),
                        SystemMessage(f"Current time: {get_current_time_ist()}"),
                        SystemMessage(
                            f"Conversation History:<conversation_history><summary>{conversation_summary}</summary> <latest_exchanges> {latest_exchanges_pretty} </latest_exchanges> </conversation_history>"
                        ),
                        HumanMessage(user_input),
                    ]
            callback = UsageMetadataCallbackHandler()
            model_response = self.llm.with_structured_output(
                SakhaResponseForASFlow
            ).invoke(chat_prompt_msgs, config={"callbacks": [callback]})
            logger.info("Successfully generated response in AS Flow")
            print(callback.usage_metadata)
            return model_response

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return {
                "replyToUser": "Sorry, I ran into an issue. Can you try again?",
                "error": f"Error generating response in ASFlow",
            }
