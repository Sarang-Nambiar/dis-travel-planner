"""
Functions to scrape specific portals regarding specific tasks (flights, accomodation, visa, etc.)
"""
import json
from config.settings import settings
import logging
from langchain.tools import tool
import http.client

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

@tool
def get_flight_details(start_country: str, destination_country: str, date: str, num_people: int):
    """
    Fetches the flight cost from a starting country to a destination country on a specified date.
    """
    # TODO: Implement here

@tool 
def get_visa_details(passport: str, destination: str) -> str:
    """
    Fetches travel visa information from: https://visa-requirement.p.rapidapi.com/v2/visa/check. Use this function to get a detailed breakdown of visa and entry requirements for one passport–destination pair.

    Make sure to pass in the passport and destination in the ISO 3166-1 alpha-2 format.
    
    passport: The country the passport was issued in. (citizenship) For example: CN for China.
    destination: The destination country in which the traveller is planning to arrive in. For example: ID for Indonesia.
    """
    url = "https://visa-requirement.p.rapidapi.com/v2/visa/check"

    headers = {
        "x-rapidapi-key": settings.rapidapi_key.get_secret_value(),
        'x-rapidapi-host': "visa-requirement.p.rapidapi.com",
        "Content-Type": "application/json",
    }
    body = {
        'passport': passport,
        'destination': destination
    }
    
    payload = json.dumps(body)

    logging.info(f"Sending request to travel buddy with passport: {passport} and desination: {destination} for visa requirements.")
    logging.info(f"Sending request to {url}")
    
    conn = http.client.HTTPSConnection("visa-requirement.p.rapidapi.com")

    conn.request("POST", "/v2/visa/check", payload, headers)

    response = conn.getresponse()
    data = response.read()
    
    requirements = data.decode("utf-8")

    logging.info(f"Status: {response.status}, Body: {response.reason}")
    
    logging.info(f"Receiving visa requirements from travel buddy: {requirements}")

    return requirements


if __name__ == "__main__":
    # get_visa_details("CN", "ID")
    pass
