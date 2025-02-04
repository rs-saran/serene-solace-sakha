from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from response_templates.conversation_state import ConversationState
from utils import exchanges_pretty, get_current_time_ist, fetch_user_preferences

class ChatEngine:
    def __init__(self, llm, bot_name="Frienn", bot_char_prompt=None):
        self.llm = llm
        self.bot_name = bot_name
        self.bot_char_prompt = bot_char_prompt or self.get_frienn_char_prompt(bot_name)
        self.conversation_history = []
        self.exchange = 0

    def get_frienn_char_prompt(self,bot_name):
        
        base_char_prompt = f'''You are {bot_name}, a kind and empathetic virtual companion designed by Friennly, designed to suggest activities to improve users mood and follow up on the activities.

        Behavior Guidelines:

        Be empathetic, respectful, and friendly.
        Respond with brief, short and clear sentences.
        If the user is felling low offering thoughtful suggestions or encouragement if not just chat like a friend
        Never provide medical, legal, or financial advice.

        Activity Suggestion Guidelines:

        Suggest the activities preferred by user if available.
        Do not suggest digital engagement activities or games.
        Ask the user if they want to do the activity now or sometime later, suggested time should be rounded.
        Do not overwhelm the user with choices and questions.
        
        Once the activity and time are chosen:

        Always double check with the user on time nd activity
        Set a reminder once the user agrees on the activity and time if it is not immediate by replying with <set_reminder> (chosen activity) at (chosen time) </set_reminder>

        After setting reminder try to end the conversation. 

        '''

        return base_char_prompt
        
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

    def chat(self,  conversation_state:ConversationState):
        user_input = conversation_state["user_input"]
        preferred_activities = conversation_state.get("preferred_activities", ["no preferences provided"])
        self.conversation_history = conversation_state.get("conversation_history", [])
        self.exchange = conversation_state.get("exchange", 0)
        
        self.generate_response(user_input, preferred_activities)
        
        return {
            "conversation_history": self.conversation_history,
            "user_input": user_input,
            "exchange": self.exchange
        }