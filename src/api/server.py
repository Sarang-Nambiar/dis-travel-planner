import logging
from typing import Annotated
from fastapi import Depends, FastAPI, Query
from src.schemas.schemas import TravelPlanDetails, TravellerProfile, State 
from src.workflow.travel_planner import TravelPlanner

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/plan")
async def get_travel_plan(traveller_profile: Annotated[TravellerProfile, Query()]):
    """
    This is the service to invoke the planning process
    """
    logging.info(f"Received: {traveller_profile} of type {type(traveller_profile)}")

    travel_planner_workflow = TravelPlanner()
    state = State(traveller_profile=traveller_profile)
    travel_plan = travel_planner_workflow.invoke_planner(state)

    return TravelPlanDetails(plan=travel_plan)
