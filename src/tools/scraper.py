"""
Functions to scrape specific portals regarding specific tasks (flights, accomodation, visa, etc.)
"""
import json
import os
import traceback
from typing import Literal
import pandas as pd
from config.settings import settings
import logging
from langchain.tools import tool
import http.client
from fast_flights import (
    FlightData,
    Passengers, 
    get_flights,
    Result
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

def format_flights(result: Result, top_k=10) -> list[dict]:
    seen = set()
    unique_flights = []
    for f in result.flights:
        key = (f.departure, f.arrival, f.price)
        if key not in seen:
            seen.add(key)
            unique_flights.append({
                "is_best": f.is_best,
                "name": f.name,
                "departure": f.departure,
                "arrival": f.arrival,
                "arrival_time_ahead": f.arrival_time_ahead,
                "duration": f.duration,
                "stops": f.stops,
                "delay": f.delay,
                "price": f.price.replace('\xa0', ' ')
            })
    
    return unique_flights[:top_k]

@tool
def get_airport_from_country(country: str, airports_data_file: str="data/airport-data.csv") -> list[list[str]] | None:
    """
    Function which provides Airport IATA code data for all cities in the provided 'country'

    Args: 
        country: The country to obtain all the Airport IATA data from.

    Returns:
        List of airports with their Name, City, IATA code and Country.

        Example - [['Udhampur Air Force Station', nan, '\\N', 'India'], ['Indira Gandhi International Airport', 'Delhi', 'DEL', 'India']]

        The special value \\N is used for "NULL" to indicate that no value is available

    Big thanks to OpenFlights for providing data completely free of charge. https://openflights.org/data.php.
    """
    if not os.path.exists(airports_data_file):
        logging.error(f"The airports data file does not exist: {airports_data_file}")
        return None

    airports_data = pd.read_csv(airports_data_file)
    
    country_wise_airports = airports_data[airports_data["Country"] == country]

    # Processing output
    output = []
    for idx, row in country_wise_airports.iterrows():
        output.append([row["Name"], row["City"], row["IATA"], row["Country"]])

    return output

@tool
def get_flight_details(from_airport: str, to_airport: str, date: str, trip: Literal["round-trip", "one-way", "multi-city"], seat: Literal["economy", "premium-economy", "business", "first"], num_people: int) -> list[dict] | None:
    """
    Fetches the flight cost from a starting country to a destination country on a specified date.

    Args:
        from_airport: The IATA airport code of the starting airport. If you are unsure of the IATA code for the starting airport, use the get_airport_from_country function to figure this out.
        to_airport: The IATA airport code of the destination airport. If you are unsure of the IATA code for the starting airport, use the get_airport_from_country function to figure this out.
        date: The date of the journey in "YYYY-MM-DD".
        num_people: Number of passengers.
        trip: Choose from the options: multi-city/one-way/round-trip 
        seat: Choose from the options: business/economy/first/premium-economy

    Returns:
        A list of dictionaries with the following keys:
            is_best - Whether Google Flights has flagged this flight as the best option based on price and convenience
            name - The airline name
            departure - The departure time
            arrival - The arrival time
            arrival_time_ahead - Whether the flight arrives on a different day (e.g. +1 means arrives the next day)
            duration - Total flight duration
            stops - Number of stopovers/layovers (e.g. "Unknown", "Nonstop", "1 stop")
            delay - Any reported delay information for the flight
            price - The ticket price including currency (e.g. "SGD 638")
    """
    try:
        res = get_flights(
            flight_data=[
                FlightData(
                    date=date,   
                    from_airport=from_airport,  
                    to_airport=to_airport,    
                ),
            ],
            seat=seat,  # business/economy/first/premium-economy
            trip=trip,  # multi-city/one-way/round-trip
            passengers=Passengers(adults=num_people),
            fetch_mode="fallback"
        )

        logging.info(f"Obtained results from the Google Flight API - {res}")

        return format_flights(res, top_k=10)

    except Exception as e:
        logging.error(f"Error occurred while trying to get the flight details: {e}")
        logging.error(f"TRACEBACK: {traceback.format_exc()}")
        return None


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
    # output = get_flight_details("ORD", "LAX", "2026-05-02", "one-way", "economy", 1)
    # output = get_airport_from_country("India")
    # print(output)
    pass
