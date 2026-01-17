import streamlit as st

# TODO: Structure this file to handle API requests, render frontend components, and modularise it.
# TODO: Manual Slider not working for budget
import streamlit as st
from datetime import datetime, timedelta
from typing import Optional

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
    
    col3, col4 = st.columns(2)
    with col3:
        # Put start country    
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
    
    cities_input = st.text_area(
        "Cities to Visit (Optional)",
        placeholder="Enter cities separated by commas (e.g., Paris, Lyon, Nice)",
        help="List the cities you plan to visit, separated by commas"
    )
    
    # Budget with dual input method
    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Budget")
        budget_method = st.radio(
            "Choose input method:",
            ["Slider", "Manual Entry"],
            horizontal=True
        )
        
        if budget_method == "Slider":
            budget = st.slider(
                "Budget (SGD)",
                min_value=0.0,
                max_value=50000.0,
                value=5000.0,
                step=100.0,
                format="$%.2f"
            )
        else:
            budget = st.number_input(
                "Budget (SGD)",
                min_value=0.0,
                max_value=1000000.0,
                value=5000.0,
                step=100.0,
                format="%.2f"
            )
    with col6:
        citizenship = st.text_input(
            "Citizenship",
            placeholder="e.g., USA, UK, Canada",
            help="Enter your citizenship country"
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
        
        if budget <= 0:
            errors.append(" Budget must be greater than 0")
        elif budget < 50:
            errors.append(" Budget seems very low. Please verify.")
        
        cities = None
        if cities_input and cities_input.strip():
            cities = [city.strip() for city in cities_input.split(',') if city.strip()]
            if len(cities) > 30:
                errors.append(" You've entered more than 20 cities. Consider reducing the list.")
        
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
                st.write(f"**Cities:** {', '.join(cities)}")
            else:
                st.write("**Cities:** Not specified")
            
            st.write(f"**Budget:** ${budget:,.2f} SGD")
            st.write(f"**Additional Requirements:** {add_reqr}")
            
            form_data = {
                "start_date": start_date,
                "end_date": end_date,
                "citizenship": citizenship.strip(),
                "start_country": start_country.strip(),
                "dest_country": dest_country.strip(),
                "cities": cities,
                "budget": budget,
                "add_reqr": add_reqr.strip()
            }
            
            st.session_state.submitted = True
            st.session_state.form_data = form_data

# Display saved data outside form if previously submitted
if st.session_state.submitted and 'form_data' in st.session_state:
    with st.expander("📋 View Previously Submitted Data"):
        st.json(st.session_state.form_data, expanded=False)
