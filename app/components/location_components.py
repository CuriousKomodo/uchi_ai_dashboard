import streamlit as st
from streamlit_folium import folium_static
from utils.map_utils import create_property_map
from utils.place_utils import get_place_icon_and_color, get_place_emoji, categorize_places
from utils.demographic_utils import (
    get_population_growth_color,
    get_deprivation_rate_color,
    get_crime_rate_color
)
from app.components.criteria_components import render_lifestyle_criteria

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
                st.metric("Crime Rate", crime_rate, delta_color=color, help="#Crimes per 1000 people")
                
        with col2:
            if demographic_stats.get('deprivation_rate') is not None:
                deprivation_rate = str(demographic_stats['deprivation_rate'])
                color = get_deprivation_rate_color(deprivation_rate)
                st.metric("Deprivation Rate", deprivation_rate, delta_color=color, help="Proportion of households reported with deprivation in at least one of the dimensions")
                
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
                st.metric("Degree Rate", degree_rate, help="Proportion of households with higher education")
        
        if neighborhood_information and neighborhood_information.get('asking_price') is not None:
            st.markdown(f"**Avg. Asking Price for {property_details['num_bedrooms']} bedrooms**: £{neighborhood_information['asking_price']}")


def render_places_of_interest_by_category(property_details):
    """Render places of interest organized by category using tables."""
    st.markdown("### 🌟 Nearby Places of Interest")
    st.markdown("within 1 km 🚶🏻‍")
    
    if property_details.get("places_of_interest"):
        places = property_details["places_of_interest"]
        
        # Show summary of place types
        place_types = {}
        for place in places:
            types = place.get('types', [])
            for place_type in types[:2]:  # Take first 2 types
                place_types[place_type] = place_types.get(place_type, 0) + 1
        
        if place_types:
            st.markdown("**Found nearby:**")
            type_summary = ", ".join([f"{count} {place_type}" for place_type, count in sorted(place_types.items(), key=lambda x: x[1], reverse=True)[:5]])
            st.markdown(f"*{type_summary}*")
        
        # Categorize places
        categorized_places = categorize_places(places)
        
        # Render each category as a table
        for category, category_places in categorized_places.items():
            st.markdown(f"#### {category} ({len(category_places)} places)")
            
            # Prepare table data
            table_data = []
            for place in category_places:
                emoji = get_place_emoji(place.get('types', []))
                name = f"{emoji} {place['name']}"
                
                rating = place.get('rating', 'N/A')
                if rating != 'N/A':
                    rating = f"⭐ {rating}"
                
                types_str = ', '.join(place.get('types', [])[:2]) if place.get('types') else 'N/A'
                
                address = place.get('address', 'N/A')
                if address != 'N/A':
                    # Show shortened address
                    address_parts = address.split(',')
                    address = ', '.join(address_parts[:2]) if len(address_parts) > 2 else address
                
                table_data.append({
                    'Name': name,
                    'Rating': rating,
                    'Type': types_str,
                    'Address': address,
                    'Place URI': place.get('place_uri', ''),
                    'Website URL': place.get('url', '')
                })
            
            # Display table
            if table_data:
                st.dataframe(
                    table_data,
                    column_config={
                        "Name": st.column_config.TextColumn("Name", width="medium"),
                        "Rating": st.column_config.TextColumn("Rating", width="small"),
                        "Type": st.column_config.TextColumn("Type", width="medium"),
                        "Address": st.column_config.TextColumn("Address", width="large"),
                        "Place URI": st.column_config.LinkColumn("Maps", width="small"),
                        "Website URL": st.column_config.LinkColumn("Website", width="small")
                    },
                    hide_index=True,
                    use_container_width=True
                )
    else:
        st.info("No places of interest data available for this property.")


def render_nearby_schools_list(nearby_schools):
    """Render nearby schools in a table format."""
    if nearby_schools:
        st.markdown("### 🏫 Nearby Schools")
        
        # Prepare table data
        table_data = []
        for school in nearby_schools:
            # Check if school is outstanding
            is_outstanding = str(school.get('rating', '')).lower() == 'outstanding'
            name = school['name']
            if is_outstanding:
                name = f"🏆 {name} (Outstanding)"
            else:
                name = f"🏫 {name}"
            
            rating = school.get('rating', 'N/A')
            if rating != 'N/A':
                rating = f"⭐ {rating}"
            
            distance = f"{school.get('distance', 'N/A')} km"
            school_type = school.get('state_or_independent', 'N/A')
            
            table_data.append({
                'Name': name,
                'Rating': rating,
                'Distance': distance,
                'Type': school_type,
                'Website URL': school.get('url', '')
            })
        
        # Display table
        if table_data:
            st.dataframe(
                table_data,
                column_config={
                    "Name": st.column_config.TextColumn("Name", width="large"),
                    "Rating": st.column_config.TextColumn("Rating", width="small"),
                    "Distance": st.column_config.TextColumn("Distance", width="small"),
                    "Type": st.column_config.TextColumn("Type", width="medium"),
                    "Website URL": st.column_config.LinkColumn("Website", width="small")
                },
                hide_index=True,
                use_container_width=True
            )

def render_nearby_supermarkets_list(nearby_supermarkets):
    """Render nearby supermarkets in a table format."""
    if nearby_supermarkets:
        st.markdown("### 🛒 Nearby Supermarkets")
        
        # Prepare table data
        table_data = []
        for supermarket in nearby_supermarkets:
            name = f"🛒 {supermarket['name']}"
            
            rating = supermarket.get('rating', 'N/A')
            if rating != 'N/A':
                rating = f"⭐ {rating}"
            
            address = supermarket.get('address', 'N/A')
            if address != 'N/A':
                # Show shortened address
                address_parts = address.split(',')
                address = ', '.join(address_parts[:2]) if len(address_parts) > 2 else address
            
            table_data.append({
                'Name': name,
                'Rating': rating,
                'Address': address,
                'Maps URL': supermarket.get('place_uri', '')
            })
        
        # Display table
        if table_data:
            st.dataframe(
                table_data,
                column_config={
                    "Name": st.column_config.TextColumn("Name", width="large"),
                    "Rating": st.column_config.TextColumn("Rating", width="small"),
                    "Address": st.column_config.TextColumn("Address", width="large"),
                    "Maps URL": st.column_config.LinkColumn("Maps", width="small")
                },
                hide_index=True,
                use_container_width=True
            )

def render_nearby_green_spaces_list(nearby_green_spaces):
    """Render nearby green spaces in a table format."""
    if nearby_green_spaces:
        st.markdown("### 🌳 Nearby Green Spaces")
        
        # Prepare table data
        table_data = []
        for green_space in nearby_green_spaces:
            name = f"🌳 {green_space['name']}"
            
            rating = green_space.get('rating', 'N/A')
            if rating != 'N/A':
                rating = f"⭐ {rating}"
            
            types_str = ', '.join(green_space.get('types', [])[:2]) if green_space.get('types') else 'N/A'
            
            address = green_space.get('address', 'N/A')
            if address != 'N/A':
                # Show shortened address
                address_parts = address.split(',')
                address = ', '.join(address_parts[:2]) if len(address_parts) > 2 else address
            
            table_data.append({
                'Name': name,
                'Rating': rating,
                'Type': types_str,
                'Address': address,
                'Maps URL': green_space.get('place_uri', '')
            })
        
        # Display table
        if table_data:
            st.dataframe(
                table_data,
                column_config={
                    "Name": st.column_config.TextColumn("Name", width="large"),
                    "Rating": st.column_config.TextColumn("Rating", width="small"),
                    "Type": st.column_config.TextColumn("Type", width="medium"),
                    "Address": st.column_config.TextColumn("Address", width="large"),
                    "Maps URL": st.column_config.LinkColumn("Maps", width="small")
                },
                hide_index=True,
                use_container_width=True
            )

def render_location_tab(property_details):
    """Render the Location tab content."""
    # Render all location-related sections
    render_neighborhood_statistics(property_details)

    st.markdown("### Location Information")
    # Create the map with all markers
    m = create_property_map(property_details)
    
    # Create two columns for map and transport info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display the map
        folium_static(m, width=800, height=500)
        
        # Add map legend
        # st.markdown("### 🗺️ Map Legend")
        # legend_cols = st.columns(4)
        #
        # with legend_cols[0]:
        #     st.markdown("""
        #     **🏠 Property** - Red home icon
        #     **🏫 Schools** - Blue graduation cap
        #     **🛒 Supermarkets** - Green shopping cart
        #     **🌳 Green Spaces** - Dark green tree
        #     """)
        #
        # with legend_cols[1]:
        #     st.markdown("""
        #     **🍽️ Restaurants** - Orange utensils
        #     **🛍️ Shopping** - Purple shopping bag
        #     **🎬 Entertainment** - Dark red film
        #     **💪 Sports/Gym** - Dark blue dumbbell
        #     """)
        #
        # with legend_cols[2]:
        #     st.markdown("""
        #     **🏥 Healthcare** - Red medkit
        #     **🚌 Transport** - Dark green bus
        #     **🏛️ Cultural** - Cadet blue landmark
        #     **🙏 Religious** - Brown pray icon
        #     """)
        #
        # with legend_cols[3]:
        #     st.markdown("""
        #     **🏦 Banking** - Dark green university
        #     **📮 Post Office** - Navy envelope
        #     **👶 Childcare** - Pink baby
        #     **📍 Other Places** - Gray map marker
        #     """)
    
    with col2:
        render_transport_info(property_details)

    # Render lifestyle criteria first (neighborhood-related)
    render_lifestyle_criteria(property_details)


    # Get neighborhood info for schools, supermarkets, and green spaces
    neighborhood_info = property_details.get("neighborhood_info", {})
    nearby_schools = neighborhood_info.get("nearby_schools", [])
    nearby_supermarkets = neighborhood_info.get("nearby_supermarkets", [])
    nearby_green_spaces = neighborhood_info.get("nearby_green_spaces", [])
    
    render_nearby_schools_list(nearby_schools)
    render_nearby_supermarkets_list(nearby_supermarkets)
    render_nearby_green_spaces_list(nearby_green_spaces)
    
    # Render places of interest by category at the bottom
    render_places_of_interest_by_category(property_details) 