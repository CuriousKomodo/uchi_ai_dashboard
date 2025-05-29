import streamlit as st
from streamlit_folium import folium_static
from utils.map_utils import create_property_map
from utils.demographic_utils import (
    get_population_growth_color,
    get_deprivation_rate_color,
    get_crime_rate_color
)

def render_transport_info(property_details):
    """Render transport information in a bordered container."""
    with st.container(border=True):
        st.markdown("### 🚉 Transport Information")
        
        # Commute time
        if property_details.get("journey") and property_details["journey"].get("duration"):
            st.markdown(f"**Commute to work:** {property_details['journey'].get('duration')} min")
        
        # Nearest stations
        if "stations" in property_details:
            st.markdown("**Nearest Stations:**")
            for station in property_details["stations"]:
                st.markdown(f"- {station['station']} ({station['distance']} miles)")

def render_neighborhood_statistics(property_details):
    """Render neighborhood statistics with color-coded metrics."""
    st.markdown("### 📊 Neighborhood Statistics")
    with st.container(border=True):
        col1, col2, col3, col4, col5 = st.columns(5)

        neighborhood_information = property_details.get("neighborhood_information")  # FIXME
        neighborhood_information = property_details.get("neighborhood_info") if not neighborhood_information else neighborhood_information
        demographic_stats = neighborhood_information.get("demographics", {}) if neighborhood_information else {}
        
        with col1:
            if demographic_stats.get('crime_rate') is not None:
                crime_rate = str(demographic_stats['crime_rate'])
                color = get_crime_rate_color(crime_rate)
                st.metric("Crime Rate", crime_rate, delta_color=color)
                st.caption("#crimes per 1000 people")
                
        with col2:
            if demographic_stats.get('deprivation_rate') is not None:
                deprivation_rate = str(demographic_stats['deprivation_rate'])
                color = get_deprivation_rate_color(deprivation_rate)
                st.metric("Deprivation Rate", deprivation_rate, delta_color=color)
                
        with col3:
            if demographic_stats.get('avg_income') is not None:
                avg_income = str(demographic_stats['avg_income'])
                # Format income properly if it doesn't have currency symbol
                if not avg_income.startswith('£') and not avg_income.startswith('$'):
                    avg_income = f"£{avg_income}"
                st.metric("Avg. Household Income", avg_income)
                
        with col4:
            if demographic_stats.get('10_year_population_growth') is not None:
                growth = str(demographic_stats['10_year_population_growth'])
                color = get_population_growth_color(growth)
                st.metric("10-Year Population Growth", growth, delta_color=color)
                
        with col5:
            if demographic_stats.get('degree_rate') is not None:
                degree_rate = str(demographic_stats['degree_rate'])
                st.metric("Degree Rate", degree_rate)
        
        if neighborhood_information and neighborhood_information.get('asking_price') is not None:
            st.markdown(f"**Avg. Asking Price for {property_details['num_bedrooms']} bedrooms**: {neighborhood_information['asking_price']}")

def render_places_of_interest(property_details):
    """Render places of interest in a grid layout."""
    st.markdown("### 🌳Nearby places that might be interesting")
    st.markdown("within 1 km 🚶🏻‍")
    if property_details.get("places_of_interest"):
        # Create a grid of cards for places of interest
        cols = st.columns(3)
        for idx, place in enumerate(property_details["places_of_interest"]):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"**{place['name']}**")
                    if place.get("rating"):
                        st.markdown(f"⭐ {place['rating']}")
                    if place.get("types"):
                        st.markdown(f"*{', '.join(place['types'][:2])}*")

def render_nearby_schools_list(nearby_schools):
    """Render nearby schools in a list format."""
    if nearby_schools:
        st.markdown("### 🏫 Nearby Schools")
        
        # Add custom CSS for outstanding schools
        st.markdown("""
            <style>
            .outstanding-school {
                background-color: #e6ffe6;
                border: 2px solid #00cc00 !important;
            }
            .outstanding-badge {
                background-color: #00cc00;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 12px;
                margin-left: 8px;
            }
            </style>
        """, unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, school in enumerate(nearby_schools):
            with cols[idx % 3]:
                # Check if school is outstanding
                is_outstanding = str(school.get('rating', '')).lower() == 'outstanding'
                container_class = "outstanding-school" if is_outstanding else ""
                
                with st.container(border=True, height=250):
                    # School name with outstanding badge if applicable
                    if is_outstanding:
                        st.markdown(f"**{school['name']}** <span class='outstanding-badge'>Outstanding</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"**{school['name']}**")
                    
                    st.markdown(f"**Distance:** {school['distance']} km")
                    if 'rating' in school:
                        st.markdown(f"**Rating:** {school['rating']}")
                    if 'state_or_independent' in school:
                        st.markdown(f"**Type:** {school['state_or_independent']}")
                    if 'url' in school:
                        st.markdown(f"[View School Website]({school['url']})")

def render_nearby_supermarkets_list(nearby_supermarkets):
    """Render nearby supermarkets in a list format."""
    if nearby_supermarkets:
        st.markdown("### 🛒 Nearby Supermarkets")
        
        cols = st.columns(3)
        for idx, supermarket in enumerate(nearby_supermarkets):
            with cols[idx % 3]:
                with st.container(border=True, height=280):
                    st.markdown(f"**{supermarket['name']}**")
                    
                    # Display image if available
                    if supermarket.get('photo_uri'):
                        try:
                            st.image(supermarket['photo_uri'], width=200)
                        except Exception as e:
                            print(f"Error loading supermarket image: {str(e)}")
                    
                    if 'rating' in supermarket:
                        st.markdown(f"**Rating:** ⭐ {supermarket['rating']}")
                    
                    if 'address' in supermarket:
                        # Show shortened address
                        address_parts = supermarket['address'].split(',')
                        short_address = ', '.join(address_parts[:2]) if len(address_parts) > 2 else supermarket['address']
                        st.markdown(f"**Address:** {short_address}")
                    
                    if 'place_uri' in supermarket:
                        st.markdown(f"[View on Google Maps]({supermarket['place_uri']})")

def render_location_tab(property_details):
    """Render the Location tab content."""
    st.markdown("### Location Information")

    # Create the map with all markers
    m = create_property_map(property_details)
    
    # Create two columns for map and transport info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display the map
        folium_static(m, width=800, height=500)
    
    with col2:
        render_transport_info(property_details)

    # Render all location-related sections
    render_neighborhood_statistics(property_details)
    render_places_of_interest(property_details)
    
    # Get neighborhood info for schools and supermarkets
    neighborhood_info = property_details.get("neighborhood_info", {})
    nearby_schools = neighborhood_info.get("nearby_schools", [])
    nearby_supermarkets = neighborhood_info.get("nearby_supermarkets", [])
    
    render_nearby_schools_list(nearby_schools)
    render_nearby_supermarkets_list(nearby_supermarkets) 