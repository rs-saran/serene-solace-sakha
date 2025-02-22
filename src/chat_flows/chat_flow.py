from abc import ABC, abstractmethod

print("inside chat flow")

class ChatFlow(ABC):
    def __init__(self, llm, bot_char_prompt):
        self.llm = llm
        self.bot_char_prompt = bot_char_prompt

    @abstractmethod
    def generate_response(self, user_input, conversation_history, preferred_activities):
        pass
