from src.response_templates.frienn_template import FriennResponseForRemFlow
from src.prompt_manager import get_activity_suggestion_prompt, get_frienn_char_prompt



class ReminderFlow(ChatFlow):
    
    def generate_response(self, user_input, conversation_history, preferred_activities):
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

        model_response = self.llm.with_structured_output(FriennResponseForRemFlow).invoke(chat_prompt_msgs)

        return model_response
