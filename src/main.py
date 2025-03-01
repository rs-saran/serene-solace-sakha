# Entry point for the Frienn
from conversation_graph import ConversationGraph, ConversationProcessor

from utils import get_llm

# Initialize the conversation graph and processor

conversation_graph = ConversationGraph(llm=get_llm()).compile()
processor = ConversationProcessor(conversation_graph)

while True:
    try:
        # Take user input
        user_input = input("You: ")
        # Check for exit conditions
        if user_input.lower() in ["exit", "quit", "bye", "q"]:
            print(
                "Frienn: Take care! Remember, I'm always here if you need someone to talk to."
            )
            break

        # Process user input
        processor.process_input(user_input, thread_id="1", user_id="dev-user")

    except Exception as e:
        print(f"An error occurred: {e}")
