"""
All pre-defined schemas
"""

from datetime import date
from pydantic import BaseModel
from pydantic import BaseModel

class TravellerProfile(BaseModel):
    start_date: date 
    end_date: date
    citizenship: str
    start_country: str
    dest_country: str
    cities: str | None = None
    budget: float
    add_reqr: str | None = None

class TravelPlanDetails(BaseModel):
    plan: str # A set of consolidated plans which would be sent back to the frontend.

class State(BaseModel):
    traveller_profile: TravellerProfile
    accoms_details: str = "Accoms Not Available"
    activity_details: str = "Activities Not Available"
    visa_details: str = "Visa Not Available"
    transport_details: str = "Transport Not Available"
    flight_details: str = "Flight Not Available"
    plan: str = ""
