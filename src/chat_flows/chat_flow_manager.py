from src.logger import get_logger


from src.chat_flows.activity_suggestion_flow import ActivitySuggestionFlow
from src.chat_flows.follow_up_flow import FollowUpFlow
from src.chat_flows.reminder_flow import ReminderFlow
from src.chat_flows.normal_chat_flow import NormalChatFlow

logger = get_logger(__name__)
class ChatFlowManager:
    # 'normal_chat', 'crisis_helpline', 'reminder', 'follow_up', 'activity_suggestion'
    def __init__(self, llm):
        self.llm = llm
        self.flows = {
            "activity_suggestion": ActivitySuggestionFlow(llm),
            "reminder": ReminderFlow(llm),
            "follow_up": FollowUpFlow(llm),
            "normal_chat": NormalChatFlow(llm)
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
                f"Chat flow '{flow_name}' not found. Defaulting to 'normal_chat'."
            )
            return self.flows['normal_chat']
