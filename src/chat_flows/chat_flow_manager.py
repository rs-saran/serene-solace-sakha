from src.logger import get_logger

logger = get_logger(__name__)
from src.chat_flows.activity_suggestion_flow import ActivitySuggestionFlow
from src.chat_flows.follow_up_flow import FollowUpFlow
from src.chat_flows.reminder_flow import ReminderFlow


class ChatFlowManager:
    def __init__(self, llm):
        self.llm = llm
        self.flows = {
            "activity_suggestion": ActivitySuggestionFlow(llm),
            "reminder": ReminderFlow(llm),
            "follow-up": FollowUpFlow(llm),
        }
        logger.info(
            "ChatFlowManager initialized with flows: %s", list(self.flows.keys())
        )

    def get_chat_flow(self, flow_name):
        if flow_name in self.flows:
            logger.info(f"Retrieving chat flow: {flow_name}")
            return self.flows[flow_name]
        else:
            logger.warning(
                f"Chat flow '{flow_name}' not found. Defaulting to 'activity_suggestion'."
            )
            return ActivitySuggestionFlow(self.llm)
