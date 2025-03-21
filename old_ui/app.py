import time
import requests
import streamlit as st
import threading
import asyncio
import websockets
import json

BASE_URL = "http://127.0.0.1:8000"  # Replace with actual API URL
WS_URL = "ws://127.0.0.1:8000/ws"  # WebSocket endpoint

# Maintain WebSocket connection globally
stop_ws = False

# Ensure session_state.messages is initialized
if "messages" not in st.session_state:
    st.session_state.messages = []  # Initialize the messages list

if "message_buffer" not in st.session_state:
    st.session_state.message_buffer = []  # Buffer for messages to be processed

def get_user_info(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    return response.json() if response.status_code == 200 else None

def add_new_user(name, age_range, preferred_activities):
    user_data = {"name": name, "age_range": age_range, "preferred_activities": preferred_activities}
    response = requests.post(f"{BASE_URL}/users/add", json=user_data)
    return response.json().get("user_id", "Error") if response.status_code == 200 else f"Error: {response.text}"

def get_user_session_count(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}/sessions")
    return response.json().get("session_count", 0) if response.status_code == 200 else 0

def get_scheduled_reminders():
    response = requests.get(f"{BASE_URL}/scheduled-reminders")
    return response.json() if response.status_code == 200 else []

async def listen_to_websocket(thread_id):
    """Listens for messages on the WebSocket and updates Streamlit UI."""
    global stop_ws
    async with websockets.connect(f"{WS_URL}/{thread_id}") as ws:  # Fixed connection
        while not stop_ws:
            try:
                data = await ws.recv()  # Receive message
                print(f"Rcvd broadcasted msg for thread_id: {data}")
                message = json.loads(data)
                sender, msg = message["sender"], message["message"]
                if "message_buffer" not in st.session_state:
                    st.session_state.message_buffer = []  # Buffer for messages to be processed
                # Add to the message buffer (not directly to session_state)
                st.session_state.message_buffer.append({"role": "assistant", "content": msg})
                # with st.chat_message("assistant"):
                #     print("inside assistant: ")
                #     st.markdown(msg)
                    # streamed_response = st.write_stream(response_generator(response))
                # Use experimental rerun to update the UI in the main thread
                st.rerun()
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket Disconnected")
                break
            except Exception as e:
                print(f"WebSocket Error: {e}")
                break

def start_websocket_listener(thread_id):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(listen_to_websocket(thread_id))

# Streamlit UI
st.set_page_config(page_title="Chat with Sakha", layout="wide")
st.title("Chat with Sakha")

with st.sidebar:
    st.header("Utils")
    action = st.radio("Choose an action:", ["Add New User", "Fetch User Info", "Check Scheduled Jobs"])

    if action == "Fetch User Info":
        fetch_user_id = st.text_input("Enter User ID:")
        if st.button("Fetch Info"):
            user_info = get_user_info(fetch_user_id)
            st.json(user_info) if user_info else st.error("User not found.")

    elif action == "Add New User":
        new_name = st.text_input("Name:")
        new_age_range = st.text_input("Age Range:")
        new_activities = st.text_area("Preferred Activities (comma-separated):").split(",")
        if st.button("Add User"):
            user_id = add_new_user(new_name, new_age_range, new_activities)
            if user_id and "Error" not in user_id:
                st.success(f"User added successfully! User ID: {user_id}")
                st.code(user_id, language="plaintext")
            else:
                st.error("Failed to add user.")

    elif action == "Check Scheduled Jobs":
        if st.button("View Scheduled Reminders"):
            jobs = get_scheduled_reminders()
            st.json(jobs) if jobs else st.error("No scheduled reminders found.")

user_id = st.text_input("Enter User ID for Chat:")
thread_id = ""

if user_id:
    session_count = get_user_session_count(user_id)
    thread_id = f"tid_{user_id}_session_{session_count + 1}"
    st.text(f"Thread ID: {thread_id}")

    if "ws_thread" not in st.session_state:
        st.session_state.ws_thread = threading.Thread(target=start_websocket_listener, args=(thread_id,), daemon=True)
        st.session_state.ws_thread.start()

# If message buffer has new messages, append them to the main message list
if st.session_state.message_buffer:
    for msg in st.session_state.message_buffer:
        st.session_state.messages.append(msg)
    # Clear the buffer after processing
    st.session_state.message_buffer = []

# Display messages from session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if user_id and thread_id:
        response = requests.post(f"{BASE_URL}/chat", json={"user_id": user_id, "thread_id": thread_id, "message": prompt})
        if response.status_code != 200:
            st.error("Error sending message.")
    else:
        st.error("Please enter a valid User ID.")
