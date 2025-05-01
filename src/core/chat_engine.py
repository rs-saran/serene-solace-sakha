from langchain_core.messages import AIMessage, HumanMessage

from src.chat_flows.chat_flow_manager import ChatFlowManager
from src.logger import get_logger
from src.response_templates.conversation_state import ConversationState
from src.utils import exchanges_pretty
from src.core.conversation_summarizer import ConversationSummarizer

logger = get_logger(__name__)


class ChatEngine:
    def __init__(self, llm, response_manager):
        self.llm = llm
        self.conversation_history = []
        self.latest_exchanges = []
        self.conversation_summary = None
        self.exchange = 0
        self.flow = None
        self.chat_flow_manager = ChatFlowManager(llm)
        self.response_manager = response_manager
        self.summarizer = ConversationSummarizer(llm)
        self.activity_details = None
        self.exc_window = 10  # for summarizer
        self.reset_exchange = 1

    def generate_response(self, user_input, user_id, thread_id, user_info):
        try:
            latest_exchanges_pretty = exchanges_pretty(self.latest_exchanges)
            # logger.info(f"latest exchanges from gen response function: {self.latest_exchanges}")
            # # logger.info(f"latest conv history from gen response function: {self.conversation_history}")
            # logger.info(f"latest exchanges from gen response function: {latest_exchanges_pretty}")
            #
            # logger.info(f"[User-{user_id}] Input: {user_input}")

            chat_flow = self.chat_flow_manager.get_chat_flow(self.flow)
            raw_model_response = chat_flow.generate_response(
                user_id, thread_id,
                self.exchange,
                user_input,
                latest_exchanges_pretty,
                user_info,
                self.conversation_summary,
                self.activity_details,
            )

            response = self.response_manager.handle_response(
                user_id, thread_id, raw_model_response
            )
            model_response = response.get("reply", "")

            logger.info(f"[User-{user_id}] Sakha Response: {model_response}")

            if response.get("activity_details", None):
                self.activity_details = response["activity_details"]

            return model_response

        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}", exc_info=True)
            return "I'm sorry, I ran into an issue. Could you try again?"

    def update_conversation_history(self, user_input, response):
        if self.exchange == 0 and self.flow in ("reminder", "follow_up"):
            self.conversation_history.append(AIMessage(content=response))
        else:
            self.conversation_history.extend(
                [HumanMessage(content=user_input), AIMessage(content=response)]
            )

    def chat(self, conversation_state: ConversationState):
        try:
            user_input = conversation_state["user_input"]
            user_id = conversation_state.get("user_id", "dummy_user_id")
            thread_id = conversation_state.get("thread_id", "dummy_thread_id")
            user_info = conversation_state.get("user_info", "no user_info")
            self.activity_details = conversation_state.get(
                "activity_details", "no activity details"
            )
            self.conversation_history = conversation_state.get(
                "conversation_history", []
            )
            self.latest_exchanges = conversation_state.get(
                "latest_exchanges", []
            )
            self.conversation_summary = conversation_state.get(
                "conversation_summary", ""
            )
            self.exchange = conversation_state.get("exchange", 0)
            self.flow = conversation_state.get("supervisor_response").pickedFlow
            # print(f"flow in chat engine: {self.flow}")
            # print(f"flow in chat engine from supervisor response: {}")
            if self.exchange > 0 and self.exchange % self.exc_window == 0:
                self.reset_exchange = self.exc_window
                # logger.info(f"latest exchanges passed from chat function: {self.latest_exchanges}")
                self.conversation_summary = self.summarizer.summarize_conversation(self.latest_exchanges, self.conversation_summary)

            self.latest_exchanges = self.conversation_history[(2 * (self.reset_exchange - 1)):]

            # print(f"latest exchanges chat function: {self.latest_exchanges}")

            logger.info(
                f"Starting conversation with User-{user_id} | Flow: {self.flow}"
            )

            model_response = self.generate_response(
                user_input, user_id, thread_id, user_info
            )

            self.update_conversation_history(user_input, str(model_response))
            self.exchange += 1

            return {
                "conversation_history": self.conversation_history,
                "user_input": user_input,
                "exchange": self.exchange,
                "activity_details": self.activity_details,
                "to_user": model_response,
                "latest_exchanges": self.latest_exchanges,
                "conversation_summary": self.conversation_summary,
                "reset_exchange": self.reset_exchange
            }

        except Exception as e:
            logger.error(f"Critical error in chat execution: {str(e)}", exc_info=True)
            return {
                "conversation_history": self.conversation_history,
                "user_input": "error",
                "exchange": self.exchange,
                "activity_details": self.activity_details,
                "to_user": "Something went wrong. Please try again later.",
            }
