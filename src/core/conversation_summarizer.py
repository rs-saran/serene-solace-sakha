from src.utils import exchanges_pretty
from src.logger import get_logger

logger = get_logger(__name__)


class ConversationSummarizer:

    def __init__(self, llm):
        """
        Initializes the ConversationSummarizer with a language model.
        """
        self.llm = llm
        self.latest_exchanges = []
        self.summary_format = """
                                Summary Format:
                                
                                1. Main Topic:
                                2. Key Things the User Said:
                                3. Key Things Sakha Said or Did:
                                4. Decisions or Plans Made:
                                5. Unresolved Topics or Follow-Ups:
                                """

    def _create_summary_prompt(self, latest_exchanges: str, conversation_summary: str) -> str:
        """
        Creates the prompt for the LLM to summarize the conversation.
        """
        if conversation_summary == "":

            prompt = f"""You are Sakha, a digital friend that chats with users about their life, goals, and feelings. 
            Please summarize the following recent conversation chunk to maintain memory and emotional continuity. 
            Fill out the 5-point summary format provided below based on the recent interaction.
    
            Recent Conversation:
            {latest_exchanges}
            
            {self.summary_format}"""

        else:

            prompt = f"""You are Sakha, a digital friend that chats with users about their life, goals, and feelings. 
                        Please summarize the following recent conversation chunk to maintain memory and emotional continuity. 
                        Update the 5-point summary provided below to include info from the recent interaction.
                        
                        Summary before the recent conversation:
                        {conversation_summary}
                        
                        Recent Conversation:
                        {latest_exchanges}
                        
                        {self.summary_format}
                        """

        return prompt

    def summarize_conversation(self, latest_exchanges, conversation_summary) -> str:
        """
        Summarizes the recent conversation history using the 5-point format.

        Args:
            latest_exchanges: A list of BaseMessage objects representing the recent turns.

        Returns:
            A string containing the 5-point summary of the conversation.
        """
        formatted_latest_exchanges = exchanges_pretty(latest_exchanges)
        prompt = self._create_summary_prompt(formatted_latest_exchanges, conversation_summary)

        logger.info(
            f"Generating summary ...  {prompt}"
        )
        try:
            summary_response = self.llm.invoke([("user", prompt)])
            logger.info(
                f"Summary generated"
            )
            return summary_response.content
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            return ""
