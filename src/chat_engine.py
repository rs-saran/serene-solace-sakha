from langchain.schema import SystemMessage, HumanMessage, AIMessage

class ChatEngine:
    def __init__(self, llm, bot_name="Frienn", bot_char_prompt=None):
        self.llm = llm
        self.bot_name = bot_name
        self.bot_char_prompt = bot_char_prompt or get_frienn_char_prompt()
        self.conversation_history = []
        self.exchange = 0
    
    def generate_response(self, user_input, preferred_activities):
        print("You:", user_input)
        
        if self.exchange == 0:
            chat_prompt_msgs = [
                SystemMessage(self.bot_char_prompt),
                SystemMessage("Introduce about yourselves to the user. Introduction can be of medium size"),
                HumanMessage(user_input)
            ]
        else:
            conversation_history_pretty = exchanges_pretty(self.conversation_history)
            chat_prompt_msgs = [
                SystemMessage(self.bot_char_prompt),
                SystemMessage(f"Activities preferred by user: {preferred_activities}"),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                HumanMessage(user_input)
            ]
        
        model_response = self.llm.invoke(chat_prompt_msgs)
        print(f"{self.bot_name}:", model_response.content)
        
        self.update_conversation_history(user_input, model_response.content)
        self.exchange += 1
        
    def update_conversation_history(self, user_input, response):
        self.conversation_history.append(HumanMessage(content=user_input))
        self.conversation_history.append(AIMessage(content=response))

    def chat(self, chat_state):
        user_input = chat_state["user_input"]
        preferred_activities = chat_state.get("preferred_activities", ["no preferences provided"])
        self.conversation_history = chat_state.get("conversation_history", [])
        self.exchange = chat_state.get("exchange", 0)
        
        self.generate_response(user_input, preferred_activities)
        
        return {
            "conversation_history": self.conversation_history,
            "user_input": user_input,
            "exchange": self.exchange
        }