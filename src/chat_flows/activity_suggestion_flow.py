from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.callbacks import UsageMetadataCallbackHandler

from src.chat_flows.chat_flow import ChatFlow
from src.logger import get_logger
from src.managers.prompt_manager import (
    get_activity_suggestion_prompt,
    get_sakha_char_prompt,
)
from src.response_templates.sakha_template import SakhaResponseForASFlow
from src.response_templates.user_situation_gauger import SituationGaugerResponse
from src.utils import get_current_time_ist, exchanges_pretty
from src.managers.memory_manager import MemoryManager

logger = get_logger(__name__)


class ActivitySuggestionFlow(ChatFlow):

    def activity_memory_retriever(self, latest_exchanges_pretty, conversation_summary, user_id):

        prompt = f"Based on the provided context gauge the user situation <context>{conversation_summary}\n{latest_exchanges_pretty}</context>"
        model_response = self.llm.with_structured_output(
            SituationGaugerResponse
        ).invoke(prompt)
        logger.info(f"Successfully gauged user situation in AS Flow: {model_response}")
        mem_manager = MemoryManager()
        user_situation = model_response.userSituation
        activity_memories = mem_manager.retrieve_activity_memories(user_situation, user_id)
        # mem_manager.close()

        return model_response, activity_memories

    def generate_response(
        self, conversation_state
    ):
        user_id = conversation_state.get("user_id", "dummy_user_id")
        user_input = conversation_state.get("user_input")
        user_info = conversation_state.get("user_info", "no user_info")

        latest_exchanges = conversation_state.get("latest_exchanges", [])
        latest_exchanges_pretty = exchanges_pretty(latest_exchanges)
        conversation_summary = conversation_state.get("conversation_summary", "")

        try:
            logger.info(
                f"Generating response for user_input in Activity suggestion flow : {user_input}"
            )
            user_situation_gauger_response, activity_memories = self.activity_memory_retriever(latest_exchanges_pretty, conversation_summary, user_id)

            if conversation_summary == "":
                chat_context = f"Conversation History:\n{latest_exchanges_pretty}"
            else:
                chat_context = f"Conversation History:<conversation_history><summary>{conversation_summary}</summary> <latest_exchanges> {latest_exchanges_pretty} </latest_exchanges> </conversation_history>"

            chat_prompt_msgs = [
                SystemMessage(get_sakha_char_prompt()),
                SystemMessage(get_activity_suggestion_prompt()),
                SystemMessage(f"User Info: {user_info}"),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(chat_context),
                HumanMessage(user_input),
            ]

            if activity_memories:
                chat_prompt_msgs.insert(3, SystemMessage("Memories:\n " + activity_memories))

            callback = UsageMetadataCallbackHandler()
            model_response = self.llm.with_structured_output(
                SakhaResponseForASFlow
            ).invoke(chat_prompt_msgs, config={"callbacks": [callback]})
            conversation_state.update(latest_sakha_response=model_response, latest_as_flow_response=model_response, latest_user_situation_gauger_response=user_situation_gauger_response)
            logger.info("Successfully generated response in AS Flow")
            print(callback.usage_metadata)
            return conversation_state

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return conversation_state
