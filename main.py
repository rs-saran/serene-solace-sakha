from fastapi import FastAPI, HTTPException
from src.core.conversation_graph import ConversationGraph
from src.core.conversation_processor import ConversationProcessor
from src.utils import get_llm
from src.managers.user_manager import UserManager

from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.postgres_checkpoint_manager import \
    PostgresCheckpointerManager

from src.managers.reminder_manager import ReminderManager
from src.managers.response_manager import ResponseManager
import signal
import uvicorn
from pydantic import BaseModel
from typing import List


app = FastAPI()

db_manager = PostgresDBManager()
checkpointer = PostgresCheckpointerManager(db_manager).get_checkpointer()
reminder_manager = ReminderManager(db_manager, base_url="http://127.0.0.1:8000")
response_manager = ResponseManager(
    reminder_manager=reminder_manager, db_manager=db_manager, 
)

conversation_graph = ConversationGraph(llm=get_llm(), response_manager=response_manager, checkpointer=checkpointer).compile()
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
                values={'user_info': user_manager.get_user_info(user_input.user_id), 'flow': 'activity_suggestion'}
            )
            active_sessions[user_input.thread_id] = True  # Mark session as active

        # Process user message
        response = processor.process_input(user_input.message, thread_id=user_input.thread_id, user_id=user_input.user_id)
        return {"response": response}

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
        # sys_input = "send a reminder to user for activity"
        # Process user message
        response = processor.process_input(user_input.message, thread_id=user_input.thread_id, user_id=user_input.user_id)
        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/follow-up/")
async def collect_feedback(user_input: UserInput):
    """Starts the follow-up flow for activity feedback."""
    try:
        conversation_graph.update_state(
            config={'configurable': {'thread_id': user_input.thread_id, 'user_id': user_input.user_id}},
            values={'flow': 'follow-up', 'exchange': 0}
        )
        # sys_input = "it's about time user completes their activity, collect feedback"
        
        # Process user message
        response = processor.process_input(user_input.message, thread_id=user_input.thread_id, user_id=user_input.user_id)
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


class UserCreateRequest(BaseModel):
    name: str
    age_range: str
    preferred_activities: List[str]  # Ensure it's a list


@app.post("/users/add")
async def add_user(user: UserCreateRequest):
    """Adds a new user."""
    user_id = user_manager.add_user(user.name, user.age_range, user.preferred_activities)
    if not user_id:
        raise HTTPException(status_code=500, detail="Failed to add user")
    return {"user_id": user_id}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
