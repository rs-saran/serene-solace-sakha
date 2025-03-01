# Helper functions (e.g., time handling, formatting)

import os
from datetime import datetime, timedelta

import pytz
from IPython.display import Image, display
from langchain_groq import ChatGroq


def get_current_time_ist():
    ist = pytz.timezone("Asia/Kolkata")  # IST timezone
    now_ist = datetime.now(ist)
    return now_ist.strftime("%Y-%m-%d %H:%M:%S %Z%z")


def get_current_time_ist_30min_lag():
    ist = pytz.timezone("Asia/Kolkata")  # IST timezone
    now_ist = datetime.now(ist) - timedelta(minutes=30)
    return now_ist.strftime("%Y-%m-%d %H:%M:%S %Z%z")


def exchanges_pretty(exchanges, summary=False):
    l = []
    c = "assistant"
    if summary:
        c = "assistant"
    for exc in exchanges:
        if exc.type == "ai":
            e = f"{c}: {exc.content}"
        else:
            e = f"{exc.type}: {exc.content}"
        l.append(e)
    return "\n".join(l)


def display_graph(graph):
    try:
        display(Image(graph.get_graph(xray=True).draw_mermaid_png()))
    except Exception as e:
        # This requires some extra dependencies and is optional
        print(f"Error: {e}")
        pass


def get_llm():
    ss_agent_key = "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"
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=ss_agent_key)

    return llm


def fetch_user_preferences():
    return ["jogging", "movies", "meditation"]


def print_directory_structure(path, indent=0):
    # Check if the given path exists
    if not os.path.exists(path):
        print("The specified path does not exist.")
        return

    # If it's a directory, walk through all its contents
    if os.path.isdir(path):
        # Skip the __pycache__ directory
        if os.path.basename(path) == "__pycache__":
            return

        print("  " * indent + f"[DIR] {os.path.basename(path)}")
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                print_directory_structure(
                    item_path, indent + 1
                )  # Recurse for directories
            else:
                print("  " * (indent + 1) + f"[FILE] {item}")
    else:
        print("The specified path is not a directory.")
