import logging
from langgraph.graph import StateGraph

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class ConversationProcessor:
    def __init__(self, conversation_graph: StateGraph):
        self.conversation_graph = conversation_graph

    def process_input(self, user_input: str, thread_id="dummy_thread_id", user_id="dummy_user_id"):
        """Process the user input through the conversation graph with logging and exception handling."""
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}

        try:
            # Process input and get the latest conversation state
            self.conversation_graph.invoke({"user_input": user_input}, config)

            # Extract response for user
            cs = self.conversation_graph.get_state(config=config)
            to_user = cs.values.get('to_user', "I'm sorry, I didn't quite understand that.")

            # Logging for debugging
            logger.info(f"[User: {user_id} | Thread: {thread_id}] Input: {user_input} | Response: {to_user}")

            return to_user

        except Exception as e:
            logger.error(f"Error processing input for user {user_id} in thread {thread_id}: {str(e)}", exc_info=True)
            return "Oops! Something went wrong. Please try again later."

