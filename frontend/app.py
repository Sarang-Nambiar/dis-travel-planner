import json

import streamlit as st
import os
from dotenv import load_dotenv, find_dotenv
from schemas import TravellerProfile
from datetime import datetime, timedelta
from typing import Optional
import requests

load_dotenv(find_dotenv())


# Browser tab configuration
st.set_page_config(page_title="Travel Planning Form", page_icon="✈️")

st.title("✈️ Travel Planning Form")
st.markdown("Please fill out the form below to help us plan your trip.")

if 'submitted' not in st.session_state:
    st.session_state.submitted = False

with st.form("travel_form"):
    st.subheader("Trip Details")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date(),
            min_value=datetime.now().date(),
            help="Select your trip start date"
        )
    
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date() + timedelta(days=7),
            min_value=datetime.now().date(),
            help="Select your trip end date"
        )
    
    col3, col4, col_start_city = st.columns(3)
    with col3:
        start_country = st.text_input(
            "Start Country",
            placeholder="e.g., USA, UK, Canada",
            help="Enter the country you are planning to embark from."
        )
    with col4:
        dest_country = st.text_input(
            "Destination Country",
            placeholder="e.g., France, Japan, Italy",
            help="Enter your destination country"
        )
    with col_start_city:
        start_city = st.text_input(
            "Start City",
            placeholder="e.g., Paris, Tokyo, Venice.",
            help="Enter your starting city to embark your trip from."
        )

    
    cities_input = st.text_area(
        "Cities to Visit (Optional)",
        placeholder="Enter cities separated by commas (e.g., Paris, Lyon, Nice)",
        help="List the cities you plan to visit, separated by commas"
    )
    
    # Budget with dual input method
    col5, col6 = st.columns(2)
    col7, col8 = st.columns(2)
    with col7:
        flight_budget = st.number_input(
            "Flight Budget (SGD)",
            min_value=0.0,
            max_value=50000.0,
            value=3000.0,
            step=100.0,
            format="%.2f",
            help="The amount you are dedicating to flight expenses."
            )
    with col8:
        accoms_budget = st.number_input(
            "Accommodation Budget (SGD)",
            min_value=0.0,
            max_value=50000.0,
            value=500.0,
            step=100.0,
            format="%.2f",
            help="The amount you are dedicating to accomodation"
            )
    with col5:
        citizenship = st.text_input(
            "Citizenship",
            placeholder="e.g., USA, UK, Canada",
            help="Enter your citizenship country"
        )

    with col6:
        num_people = st.number_input(
            "Number of people",
            help="Number of people embarking the trip.",
            min_value=0,
            max_value=20,
            value=1,
            step=1,
            )

    add_reqr = st.text_area(
        "Additional Requirements (Optional)",
        placeholder="Enter any special requirements, dietary preferences, or notes...",
        help="Describe any additional requirements for your trip"
    )
    
    submitted = st.form_submit_button("Submit Form", type="primary")
    
    if submitted:
        errors = []

        if start_date >= end_date:
            errors.append(" End date must be after start date")
        
        if (end_date - start_date).days > 365:
            errors.append(" Trip duration exceeds 365 days. Please verify.")
        
        if not citizenship or citizenship.strip() == "":
            errors.append(" Citizenship is required")
        elif len(citizenship.strip()) < 2:
            errors.append(" Citizenship must be at least 2 characters")
        
        if not dest_country or dest_country.strip() == "":
            errors.append(" Destination country is required")
        elif len(dest_country.strip()) < 2:
            errors.append(" Destination country must be at least 2 characters")
        
        if flight_budget <= 0:
            errors.append(" Budget must be greater than 0")
        elif flight_budget < 50:
            errors.append(" Budget seems very low. Please verify.")

        if accoms_budget <= 0:
            errors.append(" Budget must be greater than 0")
        elif accoms_budget < 50:
            errors.append(" Budget seems very low. Please verify.")

        if num_people <= 0:
            errors.append(" num_people must be greater than 0")
        
        cities = None
        if cities_input and cities_input.strip():
            list_cities = [city.strip() for city in cities_input.split(',') if city.strip()]
            if len(list_cities) > 30:
                errors.append(" You've entered more than 20 cities. Consider reducing the list.")
            cities = cities_input
        
        if errors:
            st.error("### Validation Errors")
            for error in errors:
                st.error(error)
        else:
            st.success("###  Form submitted successfully!")
            st.balloons()
            
            st.subheader("Submitted Information:")
            st.write(f"**Start Date:** {start_date.strftime('%B %d, %Y')}")
            st.write(f"**End Date:** {end_date.strftime('%B %d, %Y')}")
            st.write(f"**Trip Duration:** {(end_date - start_date).days} days")
            st.write(f"**Citizenship:** {citizenship}")
            st.write(f"**Destination dest_country:** {dest_country}")
            
            if cities:
                st.write(f"**Cities:** {cities}")
            else:
                st.write("**Cities:** Not specified")
            
            st.write(f"**Accoms Budget:** ${accoms_budget:,.2f} SGD")
            st.write(f"**Flight Budget:** ${flight_budget:,.2f} SGD")
            st.write(f"**Additional Requirements:** {add_reqr}")
            
            budget_dict = {
                "flight": float(flight_budget),
                "accoms": float(accoms_budget)
            }

            form_data = TravellerProfile(
            start_date=start_date,
            end_date=end_date,
            citizenship=citizenship.strip(),
            start_country=start_country.strip(),
            dest_country=dest_country.strip(),
            start_city=start_city.strip(),
            cities=cities,
            budget=json.dumps(budget_dict),
            add_reqr=add_reqr.strip(),
            num_people=num_people
            )
            
            st.session_state.submitted = True
            st.session_state.form_data = form_data

if st.session_state.submitted and "form_data" in st.session_state:
    # Call the API for backend here.
    st.toast("Planning Itineraries")
    response = requests.get(f"{os.getenv("BACKEND_ENDPOINT", "http://localhost:8000")}/plan", params=st.session_state.form_data)
    
    match(response.status_code):
        case 200:
            st.toast("Response has been received successfully.", icon="🥳")
            print("Response has been received successfully.")
            print(f"Response: {response.json()}")
        case 500:
            st.toast("Request code 500 returned. Something went wrong with the server.", icon="🚨")
            print("Request code 500 returned. Something went wrong with the server.")
        case _:
            print(f"Unexpected Request code {response.status_code} found.")
