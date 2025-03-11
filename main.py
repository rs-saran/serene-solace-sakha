from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.core.conversation_graph import ConversationGraph, ConversationProcessor
from src.utils import get_llm
from src.managers.user_manager import UserManager

from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.postgres_checkpoint_manager import \
    PostgresCheckpointerManager

from src.managers.reminder_manager import ReminderManager
from src.managers.response_manager import ResponseManager
import signal
import uvicorn




app = FastAPI()

db_manager = PostgresDBManager()
checkpointer = PostgresCheckpointerManager(db_manager).get_checkpointer()
reminder_manager = ReminderManager(db_manager)
response_manager = ResponseManager(
    reminder_manager=reminder_manager, db_manager=db_manager
)

conversation_graph = ConversationGraph(llm=get_llm(), response_manager, checkpointer).compile()
processor = ConversationProcessor(conversation_graph)

user_manager = UserManager()

# Store active users' conversation states
active_sessions = {}

class UserInput(BaseModel):
    user_id: str
    thread_id: str
    message: str

def handle_exit(*args):
    print("Shutting down gracefully...")
    db_manager.close()

# Register signal handlers
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)


# APIs

@app.post("/chat/")
async def chat(user_input: UserInput):
    """Handles user messages and returns chatbot responses."""
    try:
        # Ensure the user has an active session
        if user_input.thread_id not in active_sessions:
            # Default to activity suggestion if new user
            conversation_graph.update_state(
                config={'configurable': {'thread_id': user_input.thread_id, 'user_id': user_input.user_id}},
                values={'user_info': user_manager.get_user(user_input.user_id), 'flow': 'activity_suggestion'}
            )
            active_sessions[user_input.thread_id] = True  # Mark session as active

        # Process user message
        processor.process_input(user_input.message, thread_id=user_input.thread_id, user_id=user_input.user_id)

        # Retrieve the current state for the conversation
        cs = conversation_graph.get_state(config={'configurable': {'thread_id': user_input.thread_id, 'user_id': user_input.user_id}})

        # Get the response from the state (to_user)
        to_user = cs.values.get('to_user', "I'm sorry, I didn't quite understand that.")

        # Return the response to the user
        return {"response": to_user}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-reminder/")
async def send_reminder(user_input: UserInput):
    """Triggers reminder flow for a user."""
    try:
        conversation_graph.update_state(
            config={'configurable': {'thread_id': user_input.thread_id, 'user_id': user_input.user_id}},
            values={'flow': 'reminder', 'exchange': 0}
        )
        sys_input = "send a reminder to user for activity"
        response = processor.process_input("", thread_id=user_input.thread_id, user_id=user_input.user_id)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/collect-feedback/")
async def collect_feedback(user_input: UserInput):
    """Starts the follow-up flow for activity feedback."""
    try:
        conversation_graph.update_state(
            config={'configurable': {'thread_id': user_input.thread_id, 'user_id': user_input.user_id}},
            values={'flow': 'follow-up', 'exchange': 0}
        )
        sys_input = "it's about time user completes their activity, collect feedback"
        response = processor.process_input("", thread_id=user_input.thread_id, user_id=user_input.user_id)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/active-session-count/")
async def activce_session_count():
    """Returns the number of active sessions."""
    return {"active_sessions": len(active_sessions)}

@app.get("/users/{user_id}")
async def get_user_info(user_id: str):
    """Fetches user information by user ID."""
    user_info = user_manager.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return user_info

@app.get("/users/{user_id}/sessions")
async def get_user_session_count(user_id: str):
    """Fetches user session count by user ID."""
    user_session_info = user_manager.get_user_session_count(user_id)
    if not user_session_info:
        raise HTTPException(status_code=404, detail="User not found")
    return user_session_info


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

