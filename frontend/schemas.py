from datetime import date
from pydantic import BaseModel

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
