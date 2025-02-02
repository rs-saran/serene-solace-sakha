# Handles activity reminders

from response_templates.activity_remider_config import ActivityReminderConfig

def set_activity_reminder(chat_state:ChatState):
    conversation_history = chat_state.get("conversation_history",[])
    user_input = chat_state["user_input"]

    # print("received user-input: ", user_input)

    if len(conversation_history)<6:
        select_conv = conversation_history
    else:
        select_conv = conversation_history[-6:]

    reminder_config_extraction = f''' 
    Task: Extract the reminder configuration based on the activity and the time it was decided during the conversation.

    current_time: {get_current_time_ist()}

    Conversation Exchanges:
    <conversation>
    {select_conv}
    </conversation>
    
    '''

    reminder_config_extraction_response = llm_reminder_config.invoke(reminder_config_extraction)
    
    # print(f"<==== Setting reminder for {reminder_config_extraction_response.get("activity","None")} at {reminder_config_extraction_response.get("time",None)}")
    print(f"<==== Setting reminder for {reminder_config_extraction_response}")

    return {"reminder_status": True}


def get_reminder_llm(llm):
    return llm.with_structured_output(ActivityReminderConfig)