from abc import ABC, abstractmethod
from src.logger import get_logger

logger = get_logger(__name__)

class ChatFlow(ABC):
    def __init__(self, llm):
        if llm is None:
            raise ValueError("LLM instance is required for ChatFlow.")
        
        self.llm = llm
        logger.info(f"{self.__class__.__name__} initialized.")

    @abstractmethod
    def generate_response(self, *args, **kwargs):
        """Abstract method to be implemented by child classes."""
        pass
