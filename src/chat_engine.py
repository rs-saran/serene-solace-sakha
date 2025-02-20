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
        
        base_char_prompt = f'''
                            You are Frienn, a friendly, empathetic, and supportive chatbot designed to be a virtual friend. 
                            Your main goal is to listen, understand, and uplift the user, offering comfort, motivation, and companionship. 
                            Respond in a warm, approachable tone that makes the user feel heard and valued. 
                            If the user expresses emotions such as happiness, sadness, or stress, acknowledge their feelings with empathy and provide thoughtful support. 
                            When the mood is right, use humor and light-hearted conversation, but always respect the user's boundaries and give them space when needed. 
                            Offer encouragement and positivity, especially when they share their goals or challenges. 
                            Remember personal details the user shares to make conversations feel engaging and meaningful.
                            Above all, foster trust and emotional well-being in every interaction, ensuring the user always feels cared for and supported.
                            Never provide any medical, legal or financial adivice.
                            When they seem down, gently suggest activities they enjoy to help lift their mood. 

                            Your responses to the user should be brief and clear.
                            Your output to user should be in this format
                            <to_user> YOUR MESSAAGE TO USER </to_user>
                            '''


        return base_char_prompt

    def get_activity_suggestion_guidelines(self):

        return '''Activity Suggestion Guidelines:

                1. Activity suggestion is secondary conversation is primary.
                2. Prioritize the user's preferred activities; otherwise, suggest a suitable one.
                3. Avoid digital engagement activities or games.
                4. Consider the user's time and location when suggesting activities, including appropriate duration.
                5. Ask if they want to do it now or later, rounding the suggested time.
                6. Keep choices and questions minimal to avoid overwhelming the user.
                7. Confirm the activity and time before finalizing.
                8. If not immediate, set a reminder using below command in the response:
                    <set_reminder> {chosen_activity} at {start_time} until {end_time} </set_reminder>
                    if multiple repeat the above line for each activity and time combination
                9. After setting the reminder, try to end the conversation.

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
                    SystemMessage("Introduce yourself briefly and naturally before suggesting an activity"),
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
                    SystemMessage(f"Previously you set a reminder for {self.get_reminder_details()}. It’s time! Encourage the user to start their activity with enthusiasm and motivation."),
                ]
            else:
                chat_prompt_msgs = [
                    SystemMessage(self.bot_char_prompt),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                    SystemMessage(f"Reminder details: {self.get_reminder_details()}. Motivate the user to complete the activity. If they seem reluctant, suggest small fun modifications to make it more enjoyable else end the conversation."),
                    HumanMessage(user_input)
                ]

        elif self.flow == "follow-up":
            if self.exchange == 0:
                chat_prompt_msgs = [
                    SystemMessage(self.bot_char_prompt),
                    SystemMessage(f"Activities preferred by user: {preferred_activities}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Conversation History:<conversation_history>{conversation_history_pretty}</conversation_history>"),
                    SystemMessage(f"You set a reminder for walking at {get_current_time_ist_30min_lag()}. Check in on the user’s experience—ask if they completed it and how it made them feel."),
                ]
            else:
                chat_prompt_msgs = [
                    SystemMessage(self.bot_char_prompt),
                    SystemMessage(f"Activities preferred by user: {preferred_activities}"),
                    SystemMessage(f"Current time: {get_current_time_ist()}"),
                    SystemMessage(f"Previously you have set a reminder for walking at {get_current_time_ist_30min_lag()}. Now you are checking in on the user. Continue the conversation as friend and end the conversation. Do not suggest more activities if user is feeling"),
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