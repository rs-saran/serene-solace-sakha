from src.logger import get_logger


from src.chat_flows.activity_suggestion_flow import ActivitySuggestionFlow
from src.chat_flows.follow_up_flow import FollowUpFlow
from src.chat_flows.reminder_flow import ReminderFlow
from src.chat_flows.normal_chat_flow import NormalChatFlow

from src.response_templates.supervisor_response import SupervisorResponse
from src.response_templates.sakha_template import SakhaResponseForNCFlow, SakhaResponseForASFlow, SakhaResponseForRemFlow, SakhaResponseForFUFlow


logger = get_logger(__name__)
class ChatFlowManager:
    # 'normal_chat', 'crisis_helpline', 'reminder', 'follow_up', 'activity_suggestion'
    def __init__(self, llm):
        self.llm = llm
        self.flows = {
            "activity_suggestion": ActivitySuggestionFlow(llm),
            "reminder": ReminderFlow(llm),
            "follow_up": FollowUpFlow(llm),
            "normal_chat": NormalChatFlow(llm)
        }
        logger.info(
            "ChatFlowManager initialized with flows: %s", list(self.flows.keys())
        )

    def get_chat_flow(self, conversation_state):

        if self.is_flow_change_valid(conversation_state):
            latest_supervisor_response = conversation_state.get("latest_supervisor_response",
                                                                SupervisorResponse(pickedFlow="normal_chat",
                                                                                   reason="faced an error defaulting to normal chat"))
            flow_name = getattr(latest_supervisor_response, "pickedFlow", "normal_chat")

        else:
            flow_name = conversation_state.get("flow", "normal_chat")
            print(f"not a valid change staying in the same flow {flow_name}")

        if flow_name in self.flows:
            logger.info(f"Retrieving chat flow: {flow_name}")
            return self.flows[flow_name]
        else:
            logger.warning(
                f"Chat flow '{flow_name}' not found. Defaulting to 'normal_chat'."
            )
            return self.flows['normal_chat']

    def is_flow_change_valid(self, conversation_state):
        print(conversation_state)
        current_flow = conversation_state.get("flow", "normal_chat")
        print("\n\ncurrent_flow: ",current_flow)

        latest_supervisor_response = conversation_state.get("latest_supervisor_response", SupervisorResponse(pickedFlow="normal_chat", reason="faced an error defaulting to normal chat"))
        new_flow = getattr(latest_supervisor_response, "pickedFlow", "normal_chat")
        print("\n\nnew_flow: ", new_flow)

        if new_flow == 'crisis_helpline':
            return True

        if current_flow == "follow_up":
            latest_fu_flow_response = conversation_state.get("latest_fu_flow_response", SakhaResponseForFUFlow(replyToUser='Facing an error, please try again later', isFeedbackCollectionComplete=False, activityFeedback=None))
            print(latest_fu_flow_response)
            feedback_collection_complete = getattr(latest_fu_flow_response, "isFeedbackCollectionComplete", False)
            if feedback_collection_complete:
                print("is feedback_collection_complete = true")
                return True
            else:
                return False
        elif current_flow == "activity_suggestion":
            #TODO: Implement validity for flow change from activity_suggestion flow after better tool message implementation and retries for AS Flow
            return True

        return True

