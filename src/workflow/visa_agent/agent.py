"""
Agent that handles visa related matters.
"""
from src.schemas.schemas import State
from src.tools.scraper import get_visa_details
from src.workflow.base_agent import BaseAgent
from langchain.agents import create_agent
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

# TODO: Look into logic to trigger a direct jump to the verdict agent if getting the visa is not possible for some reason.

class VisaAgent(BaseAgent):

    def __init__(self):
        super().__init__()
        self.agent = create_agent(
            self.llm,
            tools=[get_visa_details],
            system_prompt=self.generate_prompt()
        )
    
    def generate_prompt(self):
        sys_prompt = f"""
            # Role
            You are the "Visa & Entry Orchestrator." Your goal is to determine the entry requirements for a traveler based on their passport and destination. 

            # Tool Usage Policy
            - You have access to a visa scraping tool.
            - **Constraint**: You MUST NOT guess visa requirements. You must always call the visa scraping tool using the `origin_country` and `destination_country` provided by the user to get the official JSON data.
            - **Workflow**: 
            1. Extract the origin and destination from the user's query.
            2. Call the tool.
            3. Analyze the JSON response using the "Visa Logic Hierarchy" below.
            4. Provide a human-readable summary.

            # Visa Logic Hierarchy (For JSON Interpretation)
            1. **Prioritize Exceptions**: Check `exception_rule`. If the user mentions holding a specific visa (e.g., US or Schengen), check if an exception applies first.
            2. **Digital vs. Physical**: If both a `primary_rule` (e.g., Visa on Arrival) and a `secondary_rule` (e.g., eVisa) exist, recommend the electronic/digital version as the preferred "Convenience" method.
            3. **Mandatory Steps**: Always check for `mandatory_registration` (e.g., e-Arrival cards). These are NOT visas but are required for entry.
            4. **Color Codes**:
            - Red: Visa Required (High Friction)
            - Blue: VoA/eVisa (Moderate Friction)
            - Green: Visa Free (Low Friction)
            - Yellow: eTA/Registration (Pre-arrival requirement)
            5. **Duration**: Check if the Visa would be valid for the duration of the trip. Obtain the duration from the `start_date` and `end_date` in the user query.

            # Output Requirements
            - Use bullet points for "Required Documents."
            - Explicitly state the "Stay Duration" from the `primary_rule`.
            - Always include the `link` from the JSON for eVisas or Registrations.
            - Mention `passport_validity` and local `currency` details.

            # Error Handling
            If the tool returns an error or no data, inform the user you cannot provide a definitive answer and suggest checking the official embassy link provided in the destination metadata.

            # Tone
            Professional, practical, and enthusiastic. Balance thoroughness with readability.
        """
        
        # prompt = f"Hi Deepseek! Look at this traveller info and repeat it back. {state.traveller_profile}, This is the accomodation details: {state.accoms_details}" # test prompt

        logging.info(f"Creating sys prompt for the visa agent: {sys_prompt}")
        return sys_prompt 


def visa_agent_node(state: State):
    """Facilitator function for the visa agent"""
    visa_agent = VisaAgent()
    
    prompt = f"""
    Below is some useful information that would help you determine the visa procedure.

    start_date: '{state.traveller_profile.start_date}'
    end_date: '{state.traveller_profile.end_date}'
    citizenship: '{state.traveller_profile.citizenship}'
    origin_country: '{state.traveller_profile.start_country}'
    destination_country: '{state.traveller_profile.dest_country}'
    """

    response = visa_agent.agent.invoke({"messages": [{"role": "user", "content": prompt}]})

    logging.info(f"Plan has been generated: {response}")

    return {"visa_details": str(response)}
