from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from src.core.conversation_graph import ConversationGraph
from src.core.conversation_processor import ConversationProcessor
from src.utils import get_llm
from src.managers.user_manager import UserManager
from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.postgres_checkpoint_manager import PostgresCheckpointerManager
from src.managers.reminder_manager import ReminderManager
from src.managers.response_manager import ResponseManager
import signal
import uvicorn
from pydantic import BaseModel
from typing import List, Dict
import queue

app = FastAPI()

reminder_queue = queue.Queue()
db_manager = PostgresDBManager()
checkpointer = PostgresCheckpointerManager(db_manager).get_checkpointer()
reminder_manager = ReminderManager(db_manager, reminder_queue, base_url="http://127.0.0.1:8000")
response_manager = ResponseManager(
    reminder_manager=reminder_manager, db_manager=db_manager
)

conversation_graph = ConversationGraph(llm=get_llm(), response_manager=response_manager, checkpointer=checkpointer).compile()
processor = ConversationProcessor(conversation_graph)
user_manager = UserManager()

# Store active users' conversation states
active_sessions = {}

# WebSocket Connections (thread_id -> List of WebSockets)
active_connections: Dict[str, List[WebSocket]] = {}

async def broadcast_message(thread_id: str, sender: str, message: str):
    """Send message to all active WebSocket clients for a specific thread_id."""
    if thread_id in active_connections:
        for connection in active_connections[thread_id]:
            await connection.send_json({"sender": sender, "message": message})

@app.websocket("/ws/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    """Handle WebSocket connection for a specific thread (conversation)."""
    await websocket.accept()
    if thread_id not in active_connections:
        active_connections[thread_id] = []
    active_connections[thread_id].append(websocket)

    try:
        while True:
            data = await websocket.receive_json()
            sender = data.get("sender", "Sakha")
            message = data.get("message", "")
            await broadcast_message(thread_id, sender, message)
    except WebSocketDisconnect:
        active_connections[thread_id].remove(websocket)
        if not active_connections[thread_id]:  # Cleanup if no connections left
            del active_connections[thread_id]

class UserInput(BaseModel):
    user_id: str
    thread_id: str
    message: str

def handle_exit(*args):
    print("Shutting down gracefully...")
    db_manager.close()

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

@app.post("/chat/")
async def chat(user_input: UserInput):
    """Handles user messages and returns chatbot responses."""
    try:
        if user_input.thread_id not in active_sessions:
            conversation_graph.update_state(
                config={'configurable': {'thread_id': user_input.thread_id, 'user_id': user_input.user_id}},
                values={'thread_id': user_input.thread_id, 'user_id': user_input.user_id, 'user_info': user_manager.get_user_info(user_input.user_id), 'flow': 'activity_suggestion'}
            )
            active_sessions[user_input.thread_id] = True

        response = processor.process_input(user_input.message, thread_id=user_input.thread_id, user_id=user_input.user_id)

        # Push response via WebSocket (thread-specific)
        await broadcast_message(user_input.thread_id, "Sakha", response)

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-reminder/")
async def send_reminder(user_input: UserInput):
    """Triggers reminder flow for a specific thread."""
    try:
        conversation_graph.update_state(
            config={'configurable': {'thread_id': user_input.thread_id, 'user_id': user_input.user_id}},
            values={'flow': 'reminder', 'exchange': 0}
        )
        response = processor.process_input(user_input.message, thread_id=user_input.thread_id, user_id=user_input.user_id)

        # Push reminder via WebSocket
        await broadcast_message(user_input.thread_id, "Reminder", response)

        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/active-session-count/")
async def get_active_session_count():
    """Returns the number of active sessions."""
    return {"active_sessions": len(active_sessions)}

@app.get("/users/{user_id}")
async def get_user_info(user_id: str):
    """Fetches user information by user ID."""
    user_info = user_manager.get_user_info(user_id)
    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")
    return user_info

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
