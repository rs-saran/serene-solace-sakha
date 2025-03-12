import time

import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000"  # Replace with actual API URL


def get_user_info(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}")
    if response.status_code == 200:
        return response.json()
    return None


def add_new_user(name, age_range, preferred_activities):
    user_data = {
        "name": name,
        "age_range": age_range,
        "preferred_activities": preferred_activities,  # Convert comma-separated input to a list
    }
    response = requests.post(f"{BASE_URL}/users/add", json=user_data)
    if response.status_code == 200:
        return response.json().get("user_id", "Error")
    return f"Error: {response.text}"


def get_user_session_count(user_id):
    response = requests.get(f"{BASE_URL}/users/{user_id}/sessions")
    if response.status_code == 200:
        return response.json().get("session_count", 0)
    return 0


def get_chat_response(user_id, thread_id, message):
    response = requests.post(
        f"{BASE_URL}/chat",
        json={"user_id": user_id, "thread_id": thread_id, "message": message},
    )
    if response.status_code == 200:
        return response.json().get("response", "Error")
    return "Error"


def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.set_page_config(page_title="Sakha Chat", layout="wide")
st.title("Chat with Sakha")

# Sidebar for user actions
with st.sidebar:
    st.header("User Management")
    action = st.radio("Choose an action:", ["Fetch User Info", "Add New User"])

    if action == "Fetch User Info":
        fetch_user_id = st.text_input("Enter User ID:")
        if st.button("Fetch Info"):
            user_info = get_user_info(fetch_user_id)
            if user_info:
                st.json(user_info)
            else:
                st.error("User not found.")

    elif action == "Add New User":
        new_name = st.text_input("Name:")
        new_age_range = st.text_input("Age Range:")
        new_activities = st.text_area("Preferred Activities (comma-separated):").split(
            ","
        )
        if st.button("Add User"):
            user_id = add_new_user(new_name, new_age_range, new_activities)
            if user_id:
                st.success(f"User added successfully! User ID: {user_id}")
            else:
                st.error("Failed to add user.")

# Chat UI

if "messages" not in st.session_state:
    st.session_state.messages = []

user_id = st.text_input("Enter User ID for Chat:")
thread_id = ""
if user_id:
    session_count = get_user_session_count(user_id)
    thread_id = f"tid_{user_id}_session_{session_count + 1}"
    st.text(f"Thread ID: {thread_id}")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
