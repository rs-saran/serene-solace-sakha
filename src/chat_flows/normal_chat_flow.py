from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.callbacks import UsageMetadataCallbackHandler

from src.chat_flows.chat_flow import ChatFlow
from src.logger import get_logger
from src.managers.prompt_manager import get_sakha_char_prompt
from src.response_templates.sakha_template import SakhaResponseForNCFlow, SakhaResponseForError
from src.utils import get_current_time_ist, exchanges_pretty

logger = get_logger(__name__)


class NormalChatFlow(ChatFlow):

    def generate_response(
        self, conversation_state
    ):
        user_input = conversation_state.get("user_input")
        user_info  = conversation_state.get("user_info", "no user_info")
        exchange   = conversation_state.get("exchange", 0)

        latest_exchanges = conversation_state.get("latest_exchanges", [])
        latest_exchanges_pretty = exchanges_pretty(latest_exchanges)
        conversation_summary = conversation_state.get("conversation_summary", "")

        try:
            logger.info(
                f"Generating response for user_input in Normal Chat flow : {user_input}"
            )

            if exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(f"User Info: {user_info}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(
                        "Introduce yourself briefly and naturally and check how the user is doing."
                    ),
                    HumanMessage(user_input),
                ]
            else:
                if conversation_summary == "":
                    chat_context = f"Conversation History:\n{latest_exchanges_pretty}"
                else:
                    chat_context = f"Conversation History:<conversation_history><summary>{conversation_summary}</summary> <latest_exchanges> {latest_exchanges_pretty} </latest_exchanges> </conversation_history>"

                chat_prompt_msgs = [
                    SystemMessage(get_sakha_char_prompt()),
                    SystemMessage(f"User Info: {user_info}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(chat_context),
                    HumanMessage(user_input),
                ]

            callback = UsageMetadataCallbackHandler()
            model_response = self.llm.with_structured_output(
                SakhaResponseForNCFlow
            ).invoke(chat_prompt_msgs, config={"callbacks": [callback]})
            conversation_state.update(latest_sakha_response=model_response, latest_nc_flow_response=model_response, flow="normal_chat")
            logger.info("Successfully generated response in NC Flow")
            print(callback.usage_metadata)
            return conversation_state

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            conversation_state.update(latest_sakha_response=SakhaResponseForError(replyToUser="Sorry, I ran into an issue. Can you try again?", error=f"Error generating response in NCFlow {str(e)}"), flow="normal_chat")
            return conversation_state
