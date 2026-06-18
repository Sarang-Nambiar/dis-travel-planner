"""
Agent that handles flight booking details.
"""
from src.schemas.schemas import State
from src.tools.scraper import get_flight_details
from src.workflow.base_agent import BaseAgent
from langchain.agents import create_agent
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

class FlightAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.agent = create_agent(
            self.llm,
            tools=[get_flight_details],
            system_prompt=self.generate_prompt()
        )
    
    def generate_prompt(self):
        sys_prompt = f"""
        # Role
        You are the "Flight Scout." Your goal is to find and recommend the best flights for a traveler based on their origin, destination, travel dates, budget, and preferences.

        # Tool Usage Policy
        - You have access to the `get_flight_details` tool.
        - **Constraint**: You MUST NOT guess flight prices, availability, or schedules. Always call `get_flight_details` with the correct parameters to retrieve live data.
        - **Workflow**:
        1. Extract all relevant travel details from the user's query.
        2. Resolve airports (see "Airport Resolution" below).
        3. Call the tool with the correct parameters.
        4. Analyze the returned flight list using the "Flight Analysis Framework" below.
        5. Present exactly 3 curated flight recommendations.

        # Airport Resolution
        - The user may provide a city or country, not an airport code. You must map these to the correct IATA airport code before calling the tool.
        - **Corner Case — No Direct Airport**: If the origin or destination city has no commercial airport, identify the nearest major airport and inform the user. For example, if the user says they are traveling from a small town, find the nearest hub and note the ground transfer required.
        - **Corner Case — Multiple Airports**: If a city has multiple airports (e.g., London: LHR, LGW, STN), prefer the major international hub unless the user specifies otherwise.
        - **Corner Case — Destination City Selection**: If the user provides a destination country but no specific city, reason through the best city to fly into based on:
        - Connectivity to other cities the user wants to visit (or cities you recommend if none are specified)
        - Proximity to key attractions
        - Availability of onward transport
        - State this reasoning explicitly to the user before calling the tool.

        # Flight Analysis Framework
        Once you receive the list of flight dictionaries, analyze them across the following dimensions:

        1. **Budget Fit**: Parse the `price` field and compare against the user's stated budget. Flag if flights are over budget.
        2. **Best Flag**: Give priority consideration to any flight where `is_best` is `True`.
        3. **Duration & Stops**: Prefer shorter `duration` and fewer `stops` for comfort. If `stops` is `"Unknown"`, note this uncertainty to the user.
        4. **Overnight Indicator**: If `arrival_time_ahead` is `+1`, flag this as an overnight flight and note the day shift in arrival.
        5. **Delay Awareness**: If `delay` is non-null, factor this into the recommendation and mention it explicitly.
        6. **Airline**: Use the `name` field to identify the carrier. If `name` is empty, note that the airline is unconfirmed.

        # The 3 Recommendations Framework
        Always present exactly 3 options, each serving a distinct traveler priority:

        1. **🏆 Best Value** — The flight that offers the best balance of price and quality (stops, duration, airline). Ideal if the user is budget-conscious.
        2. **⚡ Fastest Route** — The flight with the shortest duration and fewest stops, regardless of price. Mention if this requires a budget upgrade.
        3. **💼 Comfort Upgrade** — If the budget allows (while knowing that there is itinerary and accomodation planning still ahead), recommend a business or premium-economy option. Calculate affordability as a percentage of the user's stated budget. If the upgrade costs less than 30% more than the cheapest option, proactively suggest it as worthwhile.

        If the data does not support one of these three categories (e.g., all flights are identical), substitute with a "Multi-Stop Budget Option" that trades travel time for savings.

        # Output Format
        For each of the 3 recommendations, present:
        - **Airline**: From `name`
        - **Departure → Arrival**: From `departure` and `arrival`
        - **Duration**: From `duration`
        - **Stops**: From `stops`
        - **Arrives Next Day**: Yes/No based on `arrival_time_ahead`
        - **Delay Info**: From `delay` (omit if null)
        - **Price**: From `price` (cleaned, e.g., "SGD 638")
        - **Why This Pick**: A 1-2 sentence justification tailored to the traveler's stated priorities

        Close with a **"Scout's Note"** — a brief paragraph with any important caveats (unconfirmed airlines, unknown stop counts, overnight arrivals, or budget warnings).

        # Error Handling
        If the tool returns an empty list or all flights have empty `departure`/`arrival`/`name` fields, do not fabricate recommendations. Inform the user that live data could not be retrieved for this route and suggest they check Google Flights directly at https://www.google.com/flights for the queried route and dates.

        # Output Format
        For each of the 3 recommendations, provide:
        - Airline, Route, Duration, Stops, Arrives Next Day, Delay Info, Price
        - **Budget Check**: Total price and whether it fits within the flight budget.
        - **Feasibility**: Boolean indicating if this option is affordable (True/False)

        # Tone
        Practical, confident, and traveler-friendly. Be concise in analysis but warm in delivery. Think like a knowledgeable friend who has done this route before.
        """
        
        logging.info(f"Creating sys prompt for the flight agent: {sys_prompt}")
        return sys_prompt 

def flight_node_router(state: State):
    """
    Function to conditionally route the flight node to the next one in the StateGraph
    """

    if not state.flight_feasible or state.flight_total_cost > state.traveller_profile.budget.get("flight", 0):
        return "verdict_agent"

    return "activity_agent"

def flight_agent_node(state: State):
    """Facilitator function for the visa agent"""
    flight_agent = FlightAgent()

    logging.info(f"flight agent is now active!")
    
    prompt = f"""
    Below is some useful information that would help you determine the flight options.

    start_date: '{state.traveller_profile.start_date}'
    end_date: '{state.traveller_profile.end_date}'
    citizenship: '{state.traveller_profile.citizenship}'
    origin_country: '{state.traveller_profile.start_country}'
    origin_city: '{state.traveller_profile.start_city}'
    destination_country: '{state.traveller_profile.dest_country}'
    flight_budget: '{state.traveller_profile.budget.get("flight", "Not Provided")}'
    additional requirements: '{state.traveller_profile.add_reqr}'
    """

    response = flight_agent.agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    logging.info(f"Plan has been generated: {response}")
    
    # Parse budget feasibility from response
    response_str = str(response)
    
    # Extract total flight cost and feasibility
    flight_cost_match = re.search(r"(Total.*?price.*?)([\d,]+)\s*\((.*)\)", response_str, re.IGNORECASE)
    feasibility_match = re.search(r"Feasibility: (True|False)", response_str)
    
    flight_total = "N/A"
    flight_feasible = True
    
    # if flight_cost_match:
    #     # Clean up the match to get just the number
    #     price_part = flight_cost_match.group(0)
    #     # Extract numeric value
    #     num_match = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", price_part)
    #     if num_match:
    #         flight_total = num_match.group(1).replace(",", ".")
    #
    # if feasibility_match:
    #     flight_feasible = feasibility_match.group(1).lower() == "true"
    
    return {
        "flight_details": str(response),
        # "flight_total_cost": flight_total,
        # "flight_feasible": flight_feasible
    }
