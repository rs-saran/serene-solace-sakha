import streamlit as st
import requests
import time

BASE_URL = "http://your-api-endpoint.com"  # Replace with actual API URL

def get_user_session_count(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}/sessions")
    if response.status_code == 200:
        return response.json().get("session_count", 0)
    return 0

def get_chat_response(user_id, thread_id, message):
    response = requests.post(f"{BASE_URL}/chat", json={"user_id": user_id, "thread_id": thread_id, "message": message})
    if response.status_code == 200:
        return response.json().get("response", "Error")
    return "Error"

def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

st.set_page_config(page_title="Frienn Chat", layout="wide")
st.title("Frienn Chat")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# User ID input
user_id = st.text_input("Enter User ID:")
thread_id = ""
if user_id:
    session_count = get_user_session_count(user_id)
    thread_id = f"tid_{user_id}_session_{session_count + 1}"
    st.text(f"Thread ID: {thread_id}")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    if user_id and thread_id:
        response = get_chat_response(user_id, thread_id, prompt)
    else:
        response = "Please enter a valid User ID."
    
    with st.chat_message("assistant"):
        streamed_response = st.write_stream(response_generator(response))
    st.session_state.messages.append({"role": "assistant", "content": response})
