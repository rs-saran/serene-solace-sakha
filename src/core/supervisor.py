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
            select_conv: str = "",
            conversation_summary: str = "",
            flow: str = "normal_chat"
    ) -> str:
        """Generate the prompt for the supervisor based on the current and past conversation."""

        conversation_summary_insert = (
            f"Conversation summary so far:\n{conversation_summary}\n"
            if conversation_summary else ""
        )

        select_conv_insert = (
            f"{select_conv}"
            if select_conv else "This is the beginning of the conversation"
        )

        user_input_insert = (
            f"human: {user_input}\n"
            if user_input else ""
        )

        purpose_insert = "Sakha's role is to act as friend who brightens the user's day by suggesting activities or If user the user only wants to talk then then just chat like a friend respecting user boundaries"

        common_prompt_header = """
You are an autonomous agent in a mood improvement chat system supervising Sakha.
Your task is to decide the most appropriate flow for the conversation based on Sakha's role and prior context 
You must strictly follow the routing rules provided for the current flow.
        """

        flow_rules_map = {
            "normal_chat": """
        You are currently in the 'normal_chat' flow.

        Note: be very proactive to move sakha into  activity_suggestion flow don't stay normal chat flow to wait or explicit signals for activity suggestion.
        - If the users day is not bright enough Sakha should improve the their day by suggesting an activity → switch to activity_suggestion flow.
        - If the user expresses suicidal or harmful behavior → switch to crisis_helpline flow.
        - Otherwise → stay in normal_chat flow.
        """,

            "activity_suggestion": """
        You are currently in the 'activity_suggestion' flow.

        - If the user has agreed to do some activity may or may not be the one suggested by Sakha → stay in activity_suggestion flow.
        - If the user wants to chat about something related to the activity → stay in activity_suggestion flow.
        - If the user wants to talk instead of doing an activity → switch to normal_chat flow.
        - If the user wants to chat about something else until the reminder is set → switch to normal_chat flow.
        - If the user expresses suicidal or harmful behavior → switch to crisis_helpline flow.
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
        {common_prompt_header}\n
        {purpose_insert}\n
        <prior_context>
        {conversation_summary_insert}\n
        <recent_exchanges>\n
        {select_conv_insert}\n
        {user_input_insert}\n
        </recent_exchanges>\n
        <prior_context>
        <routing_rules>
        {flow_rules_map.get(flow, "")}
        </routing_rules>
        """

        return base_char_prompt.strip()

    def get_supervisor_decision(self, conversation_state: ConversationState) -> Dict:
        """Process the conversation history and current user input to get a supervisor's decision."""
        try:
            conversation_history = conversation_state.get("conversation_history", [])
            user_input = conversation_state.get("user_input", "")
            reset_exchange = conversation_state.get("reset_exchange", 1)
            latest_exchanges = conversation_history[(2 * (reset_exchange - 1)):]
            conversation_summary = conversation_state.get("conversation_summary", None)
            flow = conversation_state.get("flow", "normal_chat")

            if not user_input and flow not in ['reminder', 'follow_up']:
                logger.warning("User input is missing in conversation_state.")
                return {"supervisor_response": SupervisorResponse(pickedFlow="normal_chat",
                                                                  reason="user input is missing defaulting to normal_chat flow")}  # Default action

            latest_exchanges_pretty = exchanges_pretty(latest_exchanges)

            logger.info(f"Generating supervisor decision for input: {user_input}")
            prompt = self.get_supervisor_prompt(user_input, latest_exchanges_pretty, conversation_summary, flow)

            logger.info(
                f"=================\nPrompt used for supervisor : {prompt}\n=================="
            )

            supervisor_response = self.llm.invoke(prompt)
            logger.info(f"Supervisor Decision: {supervisor_response}")

            return {"supervisor_response": supervisor_response}

        except Exception as e:
            logger.exception(f"Error in get_supervisor_decision: {e}")
            return {"supervisor_response": "normal_chat"}  # Fallback decision
