from langchain_core.messages import AIMessage, HumanMessage

from src.chat_flows.chat_flow_manager import ChatFlowManager
from src.core.conversation_summarizer import ConversationSummarizer
from src.logger import get_logger
from src.response_templates.conversation_state import ConversationState
from src.utils import exchanges_pretty

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

    def generate_response(self, conversation_state):
        try:

            chat_flow = self.chat_flow_manager.get_chat_flow(conversation_state)

            conversation_state = chat_flow.generate_response(conversation_state)

            reply_to_user = self.response_manager.handle_response(conversation_state)

            return reply_to_user

        except Exception as e:
            logger.error(f"Error processing user input: {str(e)}", exc_info=True)
            return "Sorry, I ran into an issue. Can you try again?"

    def update_conversation_history(self, response, conversation_state):
        reminder_start = conversation_state.get("reminder_start", False)
        followup_start = conversation_state.get("followup_start", False)
        flow = conversation_state.get("flow", "normal_chat")
        conversation_history = conversation_state.get("conversation_history", [])
        user_input = conversation_state.get("user_input")
        exchange = conversation_state.get("exchange", 0)

        if (followup_start or reminder_start) and flow in ("reminder", "follow_up"):
            conversation_history.append(AIMessage(content=response))
            conversation_state.update(followup_start=False, reminder_start=False)
        else:
            conversation_history.extend(
                [HumanMessage(content=user_input), AIMessage(content=response)]
            )
        exchange += 1
        conversation_state.update(
            conversation_history=conversation_history, exchange=exchange
        )

        return conversation_state

    def chat(self, conversation_state: ConversationState):
        try:

            conversation_history = conversation_state.get("conversation_history", [])
            latest_exchanges = conversation_state.get("latest_exchanges", [])
            conversation_summary = conversation_state.get("conversation_summary", "")
            exchange = conversation_state.get("exchange", 0)
            reset_exchange = conversation_state.get("reset_exchange", 1)

            if exchange > 0 and exchange % self.exc_window == 0:
                reset_exchange = exchange
                # logger.info(f"latest exchanges passed from chat function: {self.latest_exchanges}")
                conversation_summary = self.summarizer.summarize_conversation(
                    latest_exchanges, conversation_summary
                )
                conversation_state.update(
                    reset_exchange=reset_exchange,
                    conversation_summary=conversation_summary,
                )

            latest_exchanges = conversation_history[(2 * (reset_exchange - 1)) :]
            conversation_state.update(latest_exchanges=latest_exchanges)

            reply_to_user = self.generate_response(conversation_state)
            conversation_state.update(to_user=reply_to_user)

            if reply_to_user != "Sorry, I ran into an issue. Can you try again?":
                conversation_state = self.update_conversation_history(
                    str(reply_to_user), conversation_state
                )

            return conversation_state

        except Exception as e:
            logger.error(f"Critical error in chat execution: {str(e)}", exc_info=True)
            return conversation_state
