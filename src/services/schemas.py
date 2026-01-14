"""
All pre-defined schemas
"""

from pydantic import BaseModel
from pydantic_core.core_schema import DateSchema

# TODO: Consolidate the requirements from the user.
class TravellerProfile(BaseModel):
    start_date: DateSchema 
    end_date: DateSchema
    citizenship: str
    budget: float
    add_reqr: str

# TODO: Complete this as well 
class TravelPlanDetails(BaseModel):
    visa: str
    flights: str
    accoms: str

