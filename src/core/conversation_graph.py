from typing import Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.core.chat_engine import ChatEngine
from src.core.crisis_handler import crisis_handler
# Assuming these are defined elsewhere in your project
from src.core.supervisor import Supervisor
from src.managers.postgres_checkpoint_manager import \
    PostgresCheckpointerManager
from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.reminder_manager import ReminderManager
from src.managers.response_manager import ResponseManager
from src.response_templates.conversation_state import ConversationState
from src.response_templates.supervisor_response import SupervisorResponse


# Graph Builder Class to manage the state graph and routing
class ConversationGraph:
    def __init__(self, llm):
        self.llm = llm
        self.db_manager = PostgresDBManager()
        self.checkpointer = PostgresCheckpointerManager(self.db_manager).get_checkpointer()
        self.reminder_manager = ReminderManager(self.db_manager)
        self.response_manager = ResponseManager(
            reminder_manager=self.reminder_manager, db_manager=self.db_manager
        )
        self.builder = StateGraph(ConversationState)
        self._add_nodes()
        self._add_edges()
        # self.db_manager.setup()

    def _add_nodes(self):
        """Add all nodes to the graph"""
        self.builder.add_node(
            "Supervisor", Supervisor(llm=self.llm).get_supervisor_decision
        )
        self.builder.add_node(
            "Frienn",
            ChatEngine(llm=self.llm, response_manager=self.response_manager).chat,
        )
        self.builder.add_node("crisisHandler", crisis_handler)

    def _add_edges(self):
        """Define and add edges to the graph"""
        self.builder.add_edge(START, "Supervisor")
        self.builder.add_conditional_edges("Supervisor", self._determine_route)
        self.builder.add_edge("Frienn", END)
        self.builder.add_edge("crisisHandler", END)

    def _determine_route(
        self, conversation_state: ConversationState
    ) -> Literal["Frienn", "crisisHandler"]:
        """Determine the next route based on the supervisor response"""
        supervisor_response = conversation_state.get("supervisor_response")
        picked_route = supervisor_response.pickedRoute

        if picked_route == "continue_chat":
            return "Frienn"
        elif picked_route == "crisis_helpline":
            return "crisisHandler"
        # elif picked_route == 'set_reminder':
        #     return "setReminder"
        else:
            return "Frienn"

    def compile(self):
        """Compile the final state graph with memory saver"""
        # memory = MemorySaver()
        return self.builder.compile(checkpointer=self.checkpointer)


class ConversationProcessor:
    def __init__(self, conversation_graph: StateGraph):
        self.conversation_graph = conversation_graph

    def process_input(self, user_input: str, thread_id="1", user_id="dev-user"):
        """Process the user input through the conversation graph"""
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        self.conversation_graph.invoke({"user_input": user_input}, config)
