"""Agent that handles accommodation details for the itineraries."""
import logging
from src.schemas.schemas import State
from src.schemas.schemas import State
from src.workflow.base_agent import BaseAgent
from src.tools.scraper import get_hotels
from langchain.agents import create_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class AccommodationsAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.agent = create_agent(
            self.llm,
            tools=[get_hotels],
            system_prompt=self.generate_prompt()
        )
    
    def generate_prompt(self):
        sys_prompt = f"""
        # Role
        You are the "Accommodation Scout." Your goal is to find and recommend suitable hotels and lodging for travelers visiting specific cities.

        # Context
        The user has selected a list of destination cities to visit.

        # Tool Usage Policy
        - You have access to the `get_hotels` tool.
        - **Constraint**: You MUST NOT guess hotel prices or availability. Always call `get_hotels` with the correct city name to retrieve live data.
        - **Workflow**:
        1. Identify all destination cities from the user's itinerary.
        2. For each city, call the tool to retrieve available hotels.
        3. Analyze the results and select appropriate accommodations based on budget and preferences.
        4. Present recommendations with pricing and vendor information.

        # Selection Criteria
        When evaluating hotels from the API response:
        1. **Budget Fit**: Parse the `price` field and compare against the user's stated budget. Flag if options exceed budget.
        2. **Price Comparison**: The API returns multiple vendor prices (Booking.com, Hotels.com, etc.). Note the cheapest option but also mention if premium options exist.
        3. **Vendor Diversity**: Prefer listings from multiple booking platforms to give the user choice.
        4. **Tax Transparency**: Include tax amounts as provided to show the true final cost.

        # Budget Handling
        - If the cheapest option in a city exceeds the user's budget significantly, suggest alternative cities or budget accommodations.
        - If hotels are found but all are over budget, explicitly state that premium hotels in that city may require budget adjustment.
        - Remember that hotels are assumed to be available during the travel dates specified in the traveler profile.

        # Output Format
        For each city, provide:
        - **City Name**: The destination
        - **Budget Range**: From cheapest to most expensive options found
        - **Hotel Options**: 2-3 specific hotels with:
          - Hotel name
          - Cheapest available price and vendor (e.g., "SGD 180 at Booking.com")
          - Alternative options from other vendors
        - **Why This Selection**: Brief explanation of why these options fit the traveler's needs

        # Important Note
        IMPORTANT: The hotels listed are assumed to be available during the entire travel period (from start_date to end_date in the traveler profile). If the user needs specific dates, clarify that the prices shown are the current availability and may vary by date.

        # Error Handling
        If no hotels are found for a city, inform the user and suggest that the city may be off-season or they could consider nearby cities with similar attractions.

        # Tone
        Practical, helpful, and budget-aware. Present options in a way that helps the user make informed choices based on their priorities.
        """
        
        logging.info(f"Creating sys prompt for the accommodations agent: {sys_prompt}")
        return sys_prompt


def accoms_agent_node(state: State):
    """Facilitator function for the accommodations agent."""
    accoms_agent = AccommodationsAgent()

    logging.info(f"accommodations agent is now active!")
    
    prompt = f"""
    Below is useful information that would help you determine the accommodation details:

    Destination Cities: '{state.traveller_profile.cities}'
    Budget: '{state.traveller_profile.budget.get("accoms", "Not Available")}'
    Additional Requirements: '{state.traveller_profile.add_reqr}'
    """

    response = accoms_agent.agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    logging.info(f"Accommodation details have been generated: {response}")

    return {"accoms_details": str(response)}
