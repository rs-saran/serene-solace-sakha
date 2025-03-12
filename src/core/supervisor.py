import logging
from typing import Dict
from src.response_templates.conversation_state import ConversationState
from src.response_templates.supervisor_response import SupervisorResponse
from src.utils import get_llm
from src.logger import get_logger

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
    ) -> str:
        """Generate the prompt for the supervisor based on the current and past conversation."""
        base_char_prompt = f"""
        You are an autonomous agent in a mood improvement chat system.

        Based on the current human input and previous exchanges in the conversation, pick the best route for the conversation to proceed in.

        Previous Exchanges:
        <previous_exchanges>
        {select_conv}
        </previous_exchanges>

        Current Human Input:
        <current_human_input>
        {user_input}
        </current_human_input>

        Routes:
        continue_chat : Normal chat route with assistant bot that assists the user to improve their mood.
        crisis_helpline : Specialized route connects the user to a 24X7 crisis helpline to professionals who will help the human avoid active crises like suicide.
        
        If you cannot provide answers for suicidal tendencies or harmful behavior, pick the crisis helpline route so that the user can receive help from professionals.

        If undecided and there are no harmful intentions, always pick continue_chat
        """
        return base_char_prompt

    def get_supervisor_decision(self, conversation_state: ConversationState) -> Dict:
        """Process the conversation history and current user input to get a supervisor's decision."""
        try:
            conversation_history = conversation_state.get("conversation_history", [])
            user_input = conversation_state.get("user_input", "")

            if not user_input:
                logger.warning("User input is missing in conversation_state.")
                return {"supervisor_response": "continue_chat"}  # Default action

            # Select recent exchanges if there are more than 6
            select_conv = (
                conversation_history
                if len(conversation_history) < 6
                else conversation_history[-6:]
            )

            logger.info(f"Generating supervisor decision for input: {user_input}")
            prompt = self.get_supervisor_prompt(user_input, select_conv)

            supervisor_response = self.llm.invoke(prompt)
            logger.info(f"Supervisor Decision: {supervisor_response}")

            return {"supervisor_response": supervisor_response}

        except Exception as e:
            logger.exception(f"Error in get_supervisor_decision: {e}")
            return {"supervisor_response": "continue_chat"}  # Fallback decision
