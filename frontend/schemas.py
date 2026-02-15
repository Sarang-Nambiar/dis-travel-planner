from datetime import date
from pydantic import BaseModel
from pydantic_core.core_schema import DateSchema

class TravellerProfile(BaseModel):
    start_date: date
    end_date: date
    citizenship: str
    start_country: str
    dest_country: str
    cities: str | None = None
    budget: float
    add_reqr: str | None = None
