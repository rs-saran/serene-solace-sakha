from typing import Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from src.core.chat_engine import ChatEngine
from src.core.crisis_handler import crisis_handler
from src.core.supervisor import Supervisor
from src.managers.postgres_checkpoint_manager import \
    PostgresCheckpointerManager
from src.managers.postgres_db_manager import PostgresDBManager
from src.managers.reminder_manager import ReminderManager
from src.managers.response_manager import ResponseManager
from src.response_templates.conversation_state import ConversationState
from src.response_templates.supervisor_response import SupervisorResponse
from langgraph.checkpoint.postgres import PostgresSaver


# Graph Builder Class to manage the state graph and routing
class ConversationGraph:
    def __init__(self, llm, response_manager: ResponseManager, checkpointer: PostgresSaver):
        self.llm = llm
        self.checkpointer = checkpointer
        self.response_manager = response_manager
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
            "Sakha",
            ChatEngine(llm=self.llm, response_manager=self.response_manager).chat,
        )
        self.builder.add_node("crisisHandler", crisis_handler)

    def _add_edges(self):
        """Define and add edges to the graph"""
        self.builder.add_edge(START, "Supervisor")
        self.builder.add_conditional_edges("Supervisor", self._determine_route)
        self.builder.add_edge("Sakha", END)
        self.builder.add_edge("crisisHandler", END)

    def _determine_route(
        self, conversation_state: ConversationState
    ) -> Literal["Sakha", "crisisHandler"]:
        """Determine the next route based on the supervisor response"""
        supervisor_response = conversation_state.get("supervisor_response")
        picked_route = supervisor_response.pickedRoute

        if picked_route == "continue_chat":
            return "Sakha"
        elif picked_route == "crisis_helpline":
            return "crisisHandler"
        else:
            return "Sakha"

    def compile(self):
        """Compile the final state graph with memory saver"""
        return self.builder.compile(checkpointer=self.checkpointer)



class ConversationProcessor:
    def __init__(self, conversation_graph: StateGraph):
        self.conversation_graph = conversation_graph

    def process_input(self, user_input: str, thread_id="dummy_thread_id", user_id="dummy_user_id"):
        """Process the user input through the conversation graph"""
        config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
        self.conversation_graph.invoke({"user_input": user_input}, config)
