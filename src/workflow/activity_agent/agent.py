"""
Agent that handles activity details for the itineraries.
"""
import logging
from src.schemas.schemas import State
from src.schemas.schemas import State
from src.workflow.base_agent import BaseAgent
from src.utils.utils import get_llm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


class ActivityScout(BaseAgent):

    def __init__(self):
        super().__init__()
        self.agent = None  # Will be initialized when needed

    def generate_prompt(self) -> str:
        """Generate the system prompt for the activity agent."""
        sys_prompt = f"""
        # Role
        You are the "Activity Scout." Your goal is to curate engaging activities, attractions, and experiences for travelers visiting specific cities.

        # Context
        The user has selected a few cities to travel to.

        # Guidelines
        - Focus on unique, memorable experiences tailored to the user's interests and budget.
        - Suggest a mix of popular attractions, hidden gems, cultural experiences, and relaxation options.
        - Consider the traveler's duration of stay in each city (from start_date to end_date).
        - Respect the budget constraint when recommending paid activities.

        # Activity Categories
        Curate from these diverse categories:
        - **Iconic Landmarks**: Must-see attractions, monuments, and landmarks
        - **Cultural Experiences**: Museums, galleries, historical sites, local festivals
        - **Food & Drink**: Food tours, cooking classes, markets, cafes, bars
        - **Nature & Outdoors**: Parks, hiking trails, beaches, botanical gardens
        - **Arts & Entertainment**: Theater, music venues, street performances
        - **Hands-On**: Workshops, classes, interactive experiences

        # Selection Criteria
        1. **Variety**: Ensure a good mix of activity types across the itinerary
        2. **Feasibility**: Check opening hours align with the trip dates
        3. **Budget-Friendly**: Include free/cheap options alongside premium experiences
        4. **Accessibility**: Consider if activities are suitable for the traveler's profile
        5. **Geographic Logic**: Group nearby activities to minimize travel time between them

        # Output Format
        For each city, recommend 2-3 distinct activities:
        - **Activity Name**: Clear, descriptive title
        - **Category**: Type of experience
        - **Time Required**: Estimated duration
        - **Budget**: Price range or "Free"
        - **Why Visit**: 1-2 sentence compelling description
        - **Best Time to Visit**: Seasonal timing or time of day recommendations

        Structure the output as a consolidated travel plan that the user can easily follow.
        """
        
        logging.info(f"Creating sys prompt for the activity agent: {sys_prompt}")
        return sys_prompt


def activity_agent_node(state: State):
    """Facilitator function for the activity agent"""
    activity_agent = ActivityScout()

    logging.info(f"activity agent is now active!")
    
    prompt = f"""
    Below is some useful information that would help you determine the activities to recommend:

    Start Date: '{state.traveller_profile.start_date}'
    End Date: '{state.traveller_profile.end_date}'
    Citizenship: '{state.traveller_profile.citizenship}'
    Origin Country: '{state.traveller_profile.start_country}'
    Destination Countries: '{state.traveller_profile.dest_country}'
    Origin Cities: '{state.traveller_profile.start_city}'
    Destination Cities: '{state.cities}'
    Budget: '{state.traveller_profile.budget}'
    Additional Requirements: '{state.traveller_profile.add_reqr}'
    Number of People: {state.traveller_profile.num_people}
    """

    response = activity_agent.agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    logging.info(f"Activity plan has been generated: {response}")

    return {"activity_details": str(response)}
