class FlowManager:
    def __init__(self, llm, bot_char_prompt):
        self.llm = llm
        self.bot_char_prompt = bot_char_prompt
        self.flows = {
            "activity_suggestion": ActivitySuggestionFlow(llm, bot_char_prompt),
            "reminder": ReminderFlow(llm, bot_char_prompt),
            "follow-up": FollowUpFlow(llm, bot_char_prompt)
        }

    def get_flow(self, flow_name):
        return self.flows.get(flow_name, ActivitySuggestionFlow(self.llm, self.bot_char_prompt))
