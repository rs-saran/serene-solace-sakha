from abc import ABC, abstractmethod

# print("inside chat flow")


class ChatFlow(ABC):
    def __init__(self, llm):
        self.llm = llm

    @abstractmethod
    def generate_response(self, user_input, conversation_history, preferred_activities):
        pass
