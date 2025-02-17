from response_templates.supervisor_response import SupervisorResponse
from utils import get_llm
from typing import List, Dict
from response_templates.conversation_state import ConversationState

class Supervisor:
    def __init__(self, llm):
        self.llm = llm.with_structured_output(SupervisorResponse)
    
    def get_supervisor_prompt(self, user_input: str, select_conv: str = "This is the beginning of the conversation") -> str:
        """Generate the prompt for the supervisor based on the current and past conversation."""
        base_char_prompt = f'''
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
        '''
        return base_char_prompt

    def get_supervisor_decision(self, conversation_state:ConversationState) -> Dict:
        """Process the conversation history and current user input to get a supervisor's decision."""
        conversation_history = conversation_state.get("conversation_history",[])
        user_input = conversation_state["user_input"]
        exchange = conversation_state.get("exchange",0)

        # print("received user-input: ", user_input)
        
        # Select recent exchanges if there are more than 6
        select_conv = conversation_history if len(conversation_history) < 6 else conversation_history[-6:]
        
        prompt = self.get_supervisor_prompt(user_input, select_conv)
        supervisor_response = self.llm.invoke(prompt)

        print(f"=====> Supervisor Decision: {supervisor_response} <=====")

        return {"supervisor_response": supervisor_response}



