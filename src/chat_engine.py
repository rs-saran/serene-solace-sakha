from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from response_templates.conversation_state import ConversationState
from utils import exchanges_pretty, get_current_time_ist, fetch_user_preferences, get_current_time_ist_30min_lag

class ChatEngine:
    def __init__(self, llm, bot_name="Frienn", bot_char_prompt=None):
        self.llm = llm
        self.bot_name = bot_name
        self.bot_char_prompt = self.get_frienn_char_prompt()
        self.conversation_history = []
        self.exchange = 0
        self.flow = "activity_suggestion"

    def get_frienn_char_prompt(self):
        
        base_char_prompt = f'''You are Frienn, a kind and empathetic virtual companion designed by Friendly, designed to suggest activities to improve users mood and follow up on the activities.

        Behavior Guidelines:

        Be empathetic, respectful, and friendly.
        Respond with brief, short and clear sentences.
        If the user is felling low offering thoughtful suggestions or encouragement if not just chat like a friend
        Never provide medical, legal, or financial advice.

        '''

        return base_char_prompt

    def get_activity_suggestion_guidelines(self):

        return '''Activity Suggestion Guidelines:
    
                Suggest the activities preferred by user if available else your choice.
                Do not suggest digital engagement activities or games.

                Suggest proper duration and time.
                Consider time and place the user is in for activity suggestion.

                Ask the user if they want to do the activity now or sometime later, suggested time should be rounded.
                Do not overwhelm the user with choices and questions.
                
                Once the activity and time are chosen:

                Always double check with the user on time and activity
                Set a reminder once the user agrees on the activity and time if it is not immediate by replying with <set_reminder> (chosen activity) at (chosen start time) until  (chosen end time)</set_reminder>

                After setting reminder try to end the conversation. 

                '''
                
    def get_reminder_details(self):
        return f'''Walking at {get_current_time_ist()}'''



    def generate_response(self, user_input, preferred_activities):

        conversation_history_pretty = exchanges_pretty(self.conversation_history)
        print("You:", user_input)
        
        if self.flow == "activity_suggestion":
            if self.exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(self.get_frienn_char_prompt()),
                    SystemMessage(self.get_activity_suggestion_guidelines()),
                    SystemMessage("Introduce about yourselves to the user. Introduction can be of medium size"),
                    HumanMessage(user_input)
                     ]
            else: 
                chat_prompt_msgs = [
                SystemMessage(self.get_frienn_char_prompt()),
                SystemMessage(self.get_activity_suggestion_guidelines()),
                SystemMessage(f"Activities preferred by user: {preferred_activities}"),
                SystemMessage(f"Current time: {get_current_time_ist()}"),
                SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                HumanMessage(user_input)
                            ]

        elif self.flow == "reminder":
            if self.exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(self.bot_char_prompt),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                    SystemMessage(f"Previously you have set a reminder for {self.get_reminder_details()}. Now remind the user it is time. Pump the user with motivation to complete the activity"),
                ]
            else:
                chat_prompt_msgs = [
                    SystemMessage(self.bot_char_prompt),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                    SystemMessage(f"Reminder details: {self.get_reminder_details()}. Provide the user with motivation to complete the activity. You may suggest some fun innovative additions to the activity if user is demotivated."),
                    HumanMessage(user_input)
                ]

        elif self.flow == "follow-up":
            if self.exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(self.bot_char_prompt),
                    SystemMessage(f"Activities preferred by user: {preferred_activities}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                    SystemMessage(f"Previously you have set a reminder for walking at {get_current_time_ist_30min_lag()}.  Check if they completed the activity and follow up with the user on how it went, if the user completed the activity and if it helped them improve their mood."),
                ]
            else:
                chat_prompt_msgs = [
                    SystemMessage(self.bot_char_prompt),
                    SystemMessage(f"Activities preferred by user: {preferred_activities}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Previously you have set a reminder for walking at {get_current_time_ist_30min_lag()}. Check if they completed the activity and follow up with the user on how it went, if the user completed the activity and if it helped them improve their mood."),
                    SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                    HumanMessage(user_input)
                ]


        else:
            
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
        self.flow =  conversation_state.get("flow", "activity_suggestion")
        
        self.generate_response(user_input, preferred_activities)
        
        return {
            "conversation_history": self.conversation_history,
            "user_input": user_input,
            "exchange": self.exchange
        }