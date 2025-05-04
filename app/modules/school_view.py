import os
from pathlib import Path
from typing import List, Dict

import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium



current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent

def get_schools_locations(filters) -> List[Dict]:
    """
    Get school locations based on filters.
    
    Args:
        filters: Dictionary containing filter criteria:
            - gender: str (e.g., "Mixed", "Boys", "Girls")
            - minimum_age: int
            - maximum_age: int
            - state_or_independent: str ("state" or "independent")
            - is_special: bool
            - rating: str (e.g., "Outstanding", "Good")
    
    Returns:
        List of dictionaries containing school information with coordinates
    """
    # Get the absolute path to the schools.pkl file
    schools_file = root_dir / "data" / "schools.pkl"
    
    if not schools_file.exists():
        st.error(f"Schools data file not found at {schools_file}")
        return []
    
    schools = pd.read_pickle(schools_file)
    
    # Apply filters
    if filters.get('gender'):
        schools = schools[schools['gender'] == filters['gender'].lower()]
    if filters.get('minimum_age'):
        schools = schools[schools['minimum_age'] >= filters['minimum_age']]
    if filters.get('maximum_age'):
        schools = schools[schools['maximum_age'] <= filters['maximum_age']]
    if filters.get('state_or_independent'):
        schools = schools[schools['state_or_independent'] == filters['state_or_independent'].lower()]
    if filters.get('is_special') is not None:
        schools = schools[schools['is_special'] == filters['is_special']]
    if filters.get('rating'):
        schools = schools[schools['rating'] == filters['rating'].lower()]
    
    # Format the output
    school_locations = []
    for _, school in schools.iterrows():
        info = f"{school['name']}, {school['gender']}, {school['minimum_age']}-{school['maximum_age']} years, "
        info += f"{school['state_or_independent']}, {school['rating']} ⭐"
        
        school_locations.append({
            "name": school['name'],
            "lat": school['latitude'],
            "lon": school['longitude'],
            "school": True,
            "info": info
        })
    
    return school_locations

def get_property_coordinates(shortlist: List[Dict]) -> List[Dict]:
    """
    Extract property coordinates and information from the shortlist.
    
    Args:
        shortlist: List of property dictionaries from the user's shortlist
    
    Returns:
        List of dictionaries containing property information with coordinates
    """
    property_locations = []
    
    for prop in shortlist:
        # Extract coordinates from property details
        property_details = prop.get('property_details', {})
        location = property_details.get('location', {})
        
        if not location or 'latitude' not in location or 'longitude' not in location:
            continue
            
        # Get nearest station information
        stations = prop.get('stations', [])
        nearest_station = stations[0] if stations else None
        station_info = f"Nearest station: {nearest_station['station']} ({nearest_station['distance']} miles)" if nearest_station else "No station info"
        
        # Create property info string
        info = f"£{prop['price']:,}, {prop['num_bedrooms']} bedrooms\n{station_info}"
        
        property_locations.append({
            "name": prop['address'],
            "lat": location['latitude'],
            "lon": location['longitude'],
            "school": False,
            "info": info
        })
    
    return property_locations


def school_map_view_with_properties(filters, shortlist):
    """
    Display a map showing schools and properties with filtering options.
    
    Args:
        filters: Dictionary of school filter criteria
        shortlist: List of properties from the user's shortlist
    """
    # Create filter controls at the top
    st.title("Schools & Properties Map")
    
    # Create columns for filters
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # School type filter
    with col1:
        school_type = st.selectbox(
            "School Type",
            ["All", "State", "Independent"],
            key="school_type"
        )
        if school_type != "All":
            filters['state_or_independent'] = school_type.lower()
        elif 'state_or_independent' in filters:
            del filters['state_or_independent']
    
    # Gender filter
    with col2:
        gender = st.selectbox(
            "Gender",
            ["All", "Co-ed", "Boys", "Girls"],
            key="gender"
        )
        if gender != "All":
            filters['gender'] = gender
        elif 'gender' in filters:
            del filters['gender']
    
    # Age range filter
    with col3:
        age_range = st.slider(
            "Age Range",
            min_value=3,
            max_value=24,
            value=(3, 11),
            key="age_range"
        )
        filters['minimum_age'] = age_range[0]
        filters['maximum_age'] = age_range[1]
    
    # Rating filter
    with col4:
        rating = st.multiselect(
            "Ofsted Rating",
            ["Outstanding", "Good", "Requires Improvement", "Inadequate"],
            default=["Outstanding", "Good"],
            key="rating"
        )
        if rating:
            filters['rating'] = rating[0]  # For now, just use the first selected rating
        elif 'rating' in filters:
            del filters['rating']
    
    # Special school filter
    with col5:
        special = st.checkbox("Include Special Schools", key="special")
        if special:
            filters['is_special'] = True
        elif 'is_special' in filters:
            del filters['is_special']

    # Get locations
    school_locations = get_schools_locations(filters)
    property_locations = get_property_coordinates(shortlist)

    # Create Folium map centered around London
    m = folium.Map(location=[51.5074, -0.1278], zoom_start=11)

    # Add school markers
    for loc in school_locations:
        icon = folium.Icon(color="red", icon="school", prefix="fa")
        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            tooltip=loc["name"],
            popup=loc["info"],
            icon=icon
        ).add_to(m)

    # Add property markers
    for loc in property_locations:
        icon = folium.Icon(color="blue", icon="home", prefix="fa")
        folium.Marker(
            location=[loc["lat"], loc["lon"]],
            tooltip=loc["name"],
            popup=loc["info"],
            icon=icon
        ).add_to(m)

    # Display map legend and statistics
    st.markdown("""
        ### Map Legend
        - 🏫 Red markers: Schools
        - 🏠 Blue markers: Properties
    """)
    
    # Display statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Schools Found", len(school_locations))
    with col2:
        st.metric("Properties", len(property_locations))
    
    # Display the map
    st_folium(m, width=700, height=500)


if __name__ == '__main__':
    school_map_view_with_properties()