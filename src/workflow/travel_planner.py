"""
This contains the main logic for building the planner workflow.
"""
from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from src.workflow.accoms_agent.agent import accoms_agent_node
from src.workflow.activity_agent.agent import activity_agent_node
from src.workflow.flight_agent.agent import flight_agent_node
from src.workflow.verdict_agent.agent import verdict_agent_node
from src.schemas.schemas import State
import logging

from src.workflow.visa_agent.agent import visa_agent_node

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

class TravelPlanner:

    def build_planner_workflow(self):
        """
        Adding nodes and edges to the StateGraph for invokation.
        """
        logging.info("Building workflow graph...")
        workflow = StateGraph(State)

        # creating the nodes
        workflow.add_node("visa_agent", visa_agent_node, retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0))
        workflow.add_node("flight_agent", flight_agent_node, retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0))
        workflow.add_node("activity_agent", activity_agent_node, retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0))
        workflow.add_node("accoms_agent", accoms_agent_node, retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0))
        workflow.add_node("verdict_agent", verdict_agent_node, retry_policy=RetryPolicy(max_attempts=3, initial_interval=1.0))

        # connecting the nodes
        # current graph START -> visa_agent -> flight_agent -> activity_agent -> accoms_agent -> verdict_agent -> END
        workflow.add_edge(START, "visa_agent")
        workflow.add_edge("visa_agent", "flight_agent")
        workflow.add_edge("flight_agent", "activity_agent")
        workflow.add_edge("activity_agent", "accoms_agent")
        workflow.add_edge("accoms_agent", "verdict_agent")
        workflow.add_edge("verdict_agent", END)

        return workflow.compile()

    def invoke_planner(self, state: State) -> str:
        """
        Function to invoke the travel planner workflow.
        """
        logging.info("Invoking travel planner...")
        travel_planner_agent = self.build_planner_workflow()

        logging.info("Workflow graph has been compiled! Running the workflow")
        final_state = travel_planner_agent.invoke(state)

        logging.info(f"Final plan has been generated: {final_state['plan']}")

        return final_state["plan"]
