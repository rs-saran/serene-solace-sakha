import signal

from flask import Flask, jsonify, render_template, request, send_from_directory
from flask_socketio import SocketIO, join_room, leave_room

from src.core.conversation_graph import ConversationGraph
from src.core.conversation_processor import ConversationProcessor
from src.managers.postgres_checkpoint_manager import \
    PostgresCheckpointerManager
from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.reminder_manager import ReminderManager
from src.managers.response_manager import ResponseManager
from src.managers.user_manager import UserManager
from src.utils import get_llm

db_manager = PostgresDBManager()
checkpointer = PostgresCheckpointerManager(db_manager).get_checkpointer()
reminder_manager = ReminderManager(db_manager, base_url="http://127.0.0.1:8000")
response_manager = ResponseManager(
    reminder_manager=reminder_manager, db_manager=db_manager
)

conversation_graph = ConversationGraph(
    llm=get_llm(), response_manager=response_manager, checkpointer=checkpointer
).compile()
processor = ConversationProcessor(conversation_graph)
user_manager = UserManager(db_manager)


def handle_exit(*args):
    print("Shutting down gracefully...")
    db_manager.close()


signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

active_sessions = {}

app = Flask(__name__, static_folder="ui", template_folder="ui")
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory("ui", filename)  # Serves CSS/JS correctly


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register_user", methods=["POST"])
def register_user():
    data = request.json
    name = data.get("name")
    age_range = data.get("age_range")
    preferred_activities = data.get("preferred_activities")

    if not name or not age_range:
        return jsonify({"error": "Missing required fields"}), 400

    user_id = user_manager.add_user(name, age_range, preferred_activities)
    return jsonify({"user_id": user_id})


@app.route("/scheduled-reminders/", methods=["GET"])
def get_scheduled_reminders():
    """Fetches all scheduled reminders. only for debugging"""
    return reminder_manager.list_scheduled_jobs()


@app.route("/send-reminder/", methods=["POST"])
def send_reminder():
    """Triggers reminder flow for a specific thread."""
    try:
        data = request.json
        thread_id = data.get("thread_id")
        user_id = data.get("user_id")

        if not thread_id or not user_id:
            return jsonify({"error": "Missing thread_id or user_id"}), 400

        conversation_graph.update_state(
            config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
            values={"flow": "reminder", "exchange": 0},
        )
        response = processor.process_input(
            "Reminder Triggered", thread_id=thread_id, user_id=user_id
        )

        # Send reminder via WebSocket
        socketio.emit("bot_message", {"text": f"{response}"}, room=thread_id)

        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/send-follow-up/", methods=["POST"])
def send_follow_up():
    """Triggers follow-up flow for a specific thread."""
    try:
        data = request.json
        thread_id = data.get("thread_id")
        user_id = data.get("user_id")

        if not thread_id or not user_id:
            return jsonify({"error": "Missing thread_id or user_id"}), 400

        conversation_graph.update_state(
            config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
            values={"flow": "follow-up", "exchange": 0},
        )
        response = processor.process_input(
            "Follow-up Triggered", thread_id=thread_id, user_id=user_id
        )

        # Send follow-up via WebSocket
        socketio.emit("bot_message", {"text": f"{response}"}, room=thread_id)

        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/start_session", methods=["POST"])
def start_session():
    data = request.json
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user_info = user_manager.get_user_info(user_id)
    if not user_info:
        return jsonify({"error": "Invalid User ID"}), 404

    session_count = user_manager.start_user_session(user_id)

    thread_id = f"tid_{session_count}_{user_id}"

    return jsonify({"thread_id": thread_id, "message": "Session started"})


@socketio.on("join")
def handle_join(data):
    thread_id = data.get("thread_id")
    join_room(thread_id)
    socketio.emit(
        "system_message", {"text": f"Joined thread {thread_id}"}, room=thread_id
    )


@socketio.on("leave")
def handle_leave(data):
    thread_id = data.get("thread_id")
    leave_room(thread_id)
    socketio.emit(
        "system_message", {"text": f"Left thread {thread_id}"}, room=thread_id
    )


@socketio.on("user_message")
def handle_message(data):
    thread_id = data.get("thread_id")
    user_id = data.get("user_id")
    user_message = data.get("text")

    # Handles user messages and returns chatbot responses
    if thread_id not in active_sessions:
        conversation_graph.update_state(
            config={"configurable": {"thread_id": thread_id, "user_id": user_id}},
            values={
                "thread_id": thread_id,
                "user_id": user_id,
                "user_info": user_manager.get_user_info(user_id),
                "flow": "activity_suggestion",
            },
        )
        active_sessions[thread_id] = True

    response = processor.process_input(
        user_message, thread_id=thread_id, user_id=user_id
    )

    socketio.emit("bot_message", {"text": response}, room=thread_id)


if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=8000,
        debug=True,
        use_reloader=False,
        allow_unsafe_werkzeug=True,
    )
