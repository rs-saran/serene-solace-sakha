from typing import Dict

from src.logger import get_logger
from src.response_templates.conversation_state import ConversationState
from src.response_templates.supervisor_response import SupervisorResponse
from src.utils import exchanges_pretty

logger = get_logger(__name__)


class Supervisor:
    def __init__(self, llm):
        if llm is None:
            raise ValueError("LLM instance is required for Supervisor.")
        self.llm = llm.with_structured_output(SupervisorResponse)

    def get_supervisor_prompt(
            self,
            user_input: str,
            select_conv: str = "This is the beginning of the conversation",
            conversation_summary: str = "",
            flow: str = "normal_chat"
    ) -> str:
        """Generate the prompt for the supervisor based on the current and past conversation."""

        conversation_summary_insert = (
            f"Conversation summary so far:\n{conversation_summary}\n"
            if conversation_summary else ""
        )

        common_prompt_header = """
You are an autonomous agent in a mood improvement chat system.

Your task is to decide the most appropriate flow for the conversation based on the current user message and prior context.

You must strictly follow the routing rules provided for the current flow.
        """

        flow_rules_map = {
            "normal_chat": """
        You are currently in the 'normal_chat' flow.

        - If the user expresses suicidal or harmful behavior → switch to crisis_helpline flow.
        - If it's the right time to suggest a mood-improving activity → switch to activity_suggestion flow.
        - Otherwise → stay in normal_chat flow.
        """,

            "activity_suggestion": """
        You are currently in the 'activity_suggestion' flow.

        - If the user expresses suicidal or harmful behavior → switch to crisis_helpline flow.
        - If the user prefers to talk instead of doing an activity → switch to normal_chat flow.
        - Otherwise → stay in activity_suggestion flow.
        """,

            "reminder": """
        You are currently in the 'reminder' flow.

        - If the user is demotivated and Sakha should motivate the user → stay in reminder flow.
        - If the user wants to change or do a new activity → switch to activity_suggestion flow.
        - If the user just wants someone to talk to and not do any activity → switch to normal_chat flow.
        - If the user expresses suicidal or harmful behavior → switch to crisis_helpline flow.
        - Otherwise → stay in reminder flow.
        """,

            "follow_up": """
        You are currently in the 'follow_up' flow.

        - If the user expresses suicidal or harmful behavior → switch to crisis_helpline flow.
        - If feedback (completion, enjoyment, or reason for skipping) is not yet collected → stay in follow_up flow.
        - If the user wants to continue chatting after feedback is complete → switch to normal_chat flow 
        - Otherwise → stay in follow_up flow.
        """,

            "crisis_helpline": """
        You are currently in the 'crisis_helpline' flow.

        - This is a safety-critical flow.
        - Once triggered → stay in crisis_helpline flow. Do NOT switch to any other flow under any circumstance.
        """
        }


        base_char_prompt = f"""
        {common_prompt_header}
        
        {conversation_summary_insert}
    
        Recent Exchanges:
        <recent_exchanges>
        {select_conv}
        </recent_exchanges>
    
        Current Human Input:
        <current_human_input>
        {user_input}
        </current_human_input>
        
        Routing rules:
        <routing_rules>
        {flow_rules_map.get(flow, "")}
        </routing_rules>
        """

        return base_char_prompt.strip()

    def get_supervisor_decision(self, conversation_state: ConversationState) -> Dict:
        """Process the conversation history and current user input to get a supervisor's decision."""
        try:
            # conversation_history = conversation_state.get("conversation_history", [])
            user_input = conversation_state.get("user_input", "")
            latest_exchanges = conversation_state.get("latest_exchanges", None)
            conversation_summary = conversation_state.get("conversation_summary", None)
            flow = conversation_state.get("flow", "normal_chat")

            if not user_input:
                logger.warning("User input is missing in conversation_state.")
                return {"supervisor_response": "normal_chat"}  # Default action

            latest_exchanges_pretty = exchanges_pretty(latest_exchanges)

            logger.info(f"Generating supervisor decision for input: {user_input}")
            prompt = self.get_supervisor_prompt(user_input, latest_exchanges_pretty, conversation_summary, flow)

            supervisor_response = self.llm.invoke(prompt)
            logger.info(f"Supervisor Decision: {supervisor_response}")

            return {"supervisor_response": supervisor_response}

        except Exception as e:
            logger.exception(f"Error in get_supervisor_decision: {e}")
            return {"supervisor_response": "normal_chat"}  # Fallback decision
