"""
All pre-defined schemas
"""

from datetime import date
import json
from pydantic import BaseModel, field_validator

class TravellerProfile(BaseModel):
    start_date: date
    end_date: date
    citizenship: str
    start_country: str
    dest_country: str
    start_city: str
    cities: str | None = None
    budget: str
    add_reqr: str | None = None
    num_people: int = 1

    @field_validator("budget")
    @classmethod
    def parse_budget(cls, v):
        if isinstance(v, str):
            return json.loads(v)
        return v

class TravelPlanDetails(BaseModel):
    plan: str # A set of consolidated plans which would be sent back to the frontend.

class State(BaseModel):
    traveller_profile: TravellerProfile
    accoms_details: str = "Accoms Not Available"
    accoms_total_cost: float = 0.0
    accoms_feasible: bool = False
    activity_details: str = "Activities Not Available"
    visa_details: str = "Visa Not Available"
    transport_details: str = "Transport Not Available"
    flight_details: str = "Flight Not Available"
    flight_feasible: bool = False
    flight_total_cost: float = 0.0
    plan: str = ""
