from pydantic import BaseModel
from pydantic_core.core_schema import DateSchema
from typing import Optional

class TravellerProfile(BaseModel):
    start_date: DateSchema
    end_date: DateSchema
    citizenship: str
    start_country: str
    dest_country: str
    cities: Optional[list]
    budget: float
    add_reqr: Optional[str]
