# Helper functions (e.g., time handling, formatting)

from datetime import datetime

import pytz
from IPython.display import Image, display
from langchain_groq import ChatGroq


def get_current_time_ist():
    ist = pytz.timezone("Asia/Kolkata")  # IST timezone
    now_ist = datetime.now(ist)
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
   return ['jogging','movies','meditation'] 