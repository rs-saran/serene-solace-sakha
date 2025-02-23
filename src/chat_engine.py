from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from src.response_templates.conversation_state import ConversationState
from src.utils import exchanges_pretty, get_current_time_ist, fetch_user_preferences, get_current_time_ist_30min_lag
from src.response_templates.frienn_template import FriennResponseForASFlow, FriennResponseForRemFlow, FriennResponseForFUFlow
from src.chat_flows.chat_flow_manager import ChatFlowManager

class ChatEngine:
    def __init__(self, llm):
        self.llm = llm
        self.conversation_history = []
        self.exchange = 0
        self.flow = "activity_suggestion"
        self.chat_flow_manager = ChatFlowManager(llm)


    def generate_response(self, user_input, preferred_activities):

        conversation_history_pretty = exchanges_pretty(self.conversation_history)
        print("You:", user_input)
        
        chat_flow = self.chat_flow_manager.get_chat_flow(self.flow)
        model_response = chat_flow.generate_response(self.exchange, user_input, conversation_history_pretty, preferred_activities)
        
        # model_response = self.llm.with_structured_output(FriennResponse).invoke(chat_prompt_msgs)
        print(f"Frienn:", model_response)
        
        self.update_conversation_history(user_input, str(model_response.replyToUser))
        self.exchange += 1
        
    def update_conversation_history(self, user_input, response):
        self.conversation_history.append(HumanMessage(content=user_input))
        self.conversation_history.append(AIMessage(content=response))

    def chat(self,  conversation_state:ConversationState):
        user_input = conversation_state["user_input"]
        preferred_activities = conversation_state.get("preferred_activities", ["no preferences provided"])
        self.conversation_history = conversation_state.get("conversation_history", [])
        self.exchange = conversation_state.get("exchange", 0)
        self.flow =  conversation_state.get("flow", "activity_suggestion")
        
        self.generate_response(user_input, preferred_activities)
        
        return {
            "conversation_history": self.conversation_history,
            "user_input": user_input,
            "exchange": self.exchange
        }