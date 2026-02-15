"""
Agent that handles the final verdict and compiling the travel plan if the verdict is positive.
"""

from src.schemas.schemas import State
from src.workflow.base_agent import BaseAgent
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

class VerdictAgent(BaseAgent):

    def __init__(self):
        super().__init__()
    
    def generate_prompt(self, state: State):
        prompt = f"""
        You are an expert Travel Planner AI specializing in creating feasible, optimized itineraries based on comprehensive travel data and traveler constraints.

        ## Your Task
        Analyze the provided travel information and create detailed itinerary options that respect all constraints while maximizing the travel experience.

        ## Available Information

        ### Traveler Profile
        {state.traveller_profile.model_dump()}

        ### Travel Data Provided

        #### VISA DETAILS
        {state.visa_details}

        #### FLIGHT DETAILS
        {state.flight_details}
        
        #### ACCOMODATION DETAILS
        {state.accoms_details}

        #### TRANSPORT DETAILS
        {state.transport_details}

        #### ACTIVITY DETAILS
        {state.activity_details}

        The travel data includes:
        - Visa requirements and processing times
        - Available flights (routes, times, costs)
        - Accommodation options (locations, prices, availability)
        - Inter-city transportation (modes, durations, costs)
        - Activities and attractions (descriptions, costs, time required, operating hours)

        ## Constraints to Respect
        1. **Budget**: Total trip cost must not exceed the traveler's budget
        2. **Time Frame**: Trip must fit within available dates and duration
        3. **Visa Requirements**: Account for visa processing times and validity
        4. **Traveler Preferences**: Respect stated interests, pace preferences, and restrictions
        5. **Logical Flow**: Ensure geographical coherence and minimize backtracking

        ## Your Response Structure

        ### Step 1: Feasibility Assessment
        First, analyze whether the trip is feasible:
        - Calculate minimum required budget vs. available budget
        - Check if time frame accommodates all cities + activities + transit
        - Identify any visa, timing, or logistical blockers
        - State clearly: "This trip IS/IS NOT feasible as planned"

        ### Step 2: If Feasible - Provide Itinerary Options
        Create 2-3 distinct itinerary options with:

        **For each option:**
        - **Overview**: Brief description and what makes this option unique (e.g., "Budget-focused", "Activity-packed", "Relaxed pace")
        - **Day-by-day breakdown** including:
        - Date and location
        - Accommodation (name, cost)
        - Transportation between cities (mode, time, cost)
        - Activities scheduled (with times and costs)
        - Estimated daily cost
        - **Total Cost Breakdown**: Flights + accommodation + transport + activities + buffer (10%)
        - **Pros & Cons**: Key advantages and trade-offs of this option

        ### Step 3: Recommendations & Considerations
        - Money-saving tips specific to this itinerary
        - Booking priorities and optimal timing
        - Flexibility suggestions (what can be adjusted if needed)
        - Important reminders (visa deadlines, peak seasons, etc.)

        ## Guidelines
        - Be specific with numbers: exact costs, times, and durations
        - Prioritize realistic timing (include buffer for check-ins, meals, rest)
        - If the trip is NOT feasible, explain why and suggest modifications (reduce cities, extend duration, increase budget, etc.)
        - Consider traveler energy levels (don't over-schedule)
        - Flag any assumptions you're making about the data

        ## Tone
        Professional, practical, and enthusiastic. Balance thoroughness with readability.
        """
        
        # prompt = f"Hi Deepseek! Look at this traveller info and repeat it back. {state.traveller_profile}, This is the accomodation details: {state.accoms_details}" # test prompt

        logging.info(f"Prompting the verdict agent: {prompt}")
        return prompt

def verdict_agent_node(state: State):
    """Facilitator function for the verdict agent"""
    agent = VerdictAgent()
    prompt = agent.generate_prompt(state)

    # TODO: invoke the agent and then pass the answer to the plan attribute of state
    response = agent.llm.invoke(prompt)

    logging.info(f"Plan has been generated: {response}")

    return {"plan": str(response.content)}
