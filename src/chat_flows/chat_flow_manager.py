from src.chat_flows.activity_suggestion_flow import ActivitySuggestionFlow
from src.chat_flows.reminder_flow import ReminderFlow
from src.chat_flows.follow_up_flow import FollowUpFlow

class ChatFlowManager:
    def __init__(self, llm):
        self.llm = llm
        self.flows = {
            "activity_suggestion": ActivitySuggestionFlow(llm),
            "reminder": ReminderFlow(llm),
            "follow-up": FollowUpFlow(llm)
        }

    def get_chat_flow(self, flow_name):
        return self.flows.get(flow_name, ActivitySuggestionFlow(self.llm))
