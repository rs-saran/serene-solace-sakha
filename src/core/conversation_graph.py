from typing import Literal

from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.graph import END, START, StateGraph

from src.core.chat_engine import ChatEngine
from src.core.crisis_handler import crisis_handler
from src.core.supervisor import Supervisor
from src.logger import get_logger
from src.managers.response_manager import ResponseManager
from src.response_templates.conversation_state import ConversationState

logger = get_logger(__name__)


class ConversationGraph:
    def __init__(
        self, llm, response_manager: ResponseManager, checkpointer: PostgresSaver
    ):
        self.llm = llm
        self.checkpointer = checkpointer
        self.response_manager = response_manager
        self.builder = StateGraph(ConversationState)
        self._add_nodes()
        self._add_edges()

    def _add_nodes(self):
        """Add all nodes to the graph."""
        self.builder.add_node(
            "Supervisor", Supervisor(llm=self.llm).get_supervisor_decision
        )
        self.builder.add_node(
            "Sakha",
            ChatEngine(llm=self.llm, response_manager=self.response_manager).chat,
        )
        self.builder.add_node("crisisHandler", crisis_handler)

    def _add_edges(self):
        """Define and add edges to the graph."""
        self.builder.add_edge(START, "Supervisor")
        self.builder.add_conditional_edges("Supervisor", self._determine_route)
        self.builder.add_edge("Sakha", END)
        self.builder.add_edge("crisisHandler", END)

    def _determine_route(
        self, conversation_state: ConversationState
    ) -> Literal["Sakha", "crisisHandler"]:
        """Determine the next route based on the supervisor response."""
        supervisor_response = conversation_state.get("latest_supervisor_response")

        if not supervisor_response:
            logger.warning("Supervisor response missing. Defaulting to Sakha.")
            return "Sakha"

        picked_flow = supervisor_response.pickedFlow
        logger.info(f"Supervisor picked route: {picked_flow}")

        if picked_flow == "crisis_helpline":
            return "crisisHandler"
        # elif picked_flow in ['normal_chat', 'reminder', 'follow_up', 'activity_suggestion']:
        # conversation_state.update(flow=picked_flow)
        # logger.info(f"Updated the flow in CS: {conversation_state.get('flow', 'error: not present')}")
        return "Sakha"

    def compile(self):
        """Compile the final state graph with memory saver."""
        logger.info("Compiling the conversation graph.")
        return self.builder.compile(checkpointer=self.checkpointer)
