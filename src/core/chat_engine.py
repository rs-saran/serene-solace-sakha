from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage,
                                     ToolMessage)

from src.chat_flows.chat_flow_manager import ChatFlowManager
from src.response_templates.conversation_state import ConversationState
from src.response_templates.sakha_template import (SakhaResponseForASFlow,
                                                    SakhaResponseForFUFlow,
                                                    SakhaResponseForRemFlow)
from src.utils import (exchanges_pretty,
                       get_current_time_ist, get_current_time_ist_30min_lag)


class ChatEngine:
    def __init__(self, llm, response_manager):
        self.llm = llm
        self.conversation_history = []
        self.exchange = 0
        self.flow = "activity_suggestion"
        self.chat_flow_manager = ChatFlowManager(llm)
        self.response_manager = response_manager
        self.activity_details = None

    def generate_response(self, user_input, user_id, thread_id, user_info):

        conversation_history_pretty = exchanges_pretty(self.conversation_history)
        print("You:", user_input)

        chat_flow = self.chat_flow_manager.get_chat_flow(self.flow)
        raw_model_response = chat_flow.generate_response(
            self.exchange, user_input, conversation_history_pretty, user_info, self.activity_details
        )

        response = self.response_manager.handle_response(user_id, thread_id, raw_model_response)

        model_response = response.get("reply", "")

        print(f"Sakha:", model_response)

        self.update_conversation_history(user_input, str(model_response))
        self.exchange += 1

        if response.get("activity_details", None):
            
            self.activity_details = response.get("activity_details")

        return model_response

    def update_conversation_history(self, user_input, response):
        self.conversation_history.append(HumanMessage(content=user_input))
        self.conversation_history.append(AIMessage(content=response))

    def chat(self, conversation_state: ConversationState):
        user_input = conversation_state["user_input"]
        user_id = conversation_state.get("user_id","dummy_user_id")
        thread_id = conversation_state.get("thread_id","dummy_thread_id")
        # preferred_activities = conversation_state.get(
        #     "preferred_activities", ["no preferences provided"]
        # )
        user_info = conversation_state.get(
            "user_info", "no user_info"
        )
        self.activity_details = conversation_state.get(
            "activity_details", {"activity": None}
        )
        self.conversation_history = conversation_state.get("conversation_history", [])
        self.exchange = conversation_state.get("exchange", 0)
        self.flow = conversation_state.get("flow", "activity_suggestion")

        # self.generate_response(user_input, user_id, thread_id, preferred_activities)
        model_response = self.generate_response(user_input, user_id, thread_id, user_info)

        return {
            "conversation_history": self.conversation_history,
            "user_input": user_input,
            "exchange": self.exchange,
            "activity_details": self.activity_details,
            "to_user": model_response
        }
