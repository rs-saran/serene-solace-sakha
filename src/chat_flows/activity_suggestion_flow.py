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
from src.utils import get_current_time_ist
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

        return activity_memories



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
                f"Generating response for user_input in Activity suggestion flow : {user_input}"
            )
            activity_memories = self.activity_memory_retriever(latest_exchanges_pretty,conversation_summary,user_id)
            if activity_memories:

                if conversation_summary == "":
                    chat_prompt_msgs = [
                        SystemMessage(get_sakha_char_prompt()),
                        SystemMessage(get_activity_suggestion_prompt()),
                        SystemMessage(f"User Info: {user_info}"),
                        SystemMessage("Memories:\n " + activity_memories),
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
