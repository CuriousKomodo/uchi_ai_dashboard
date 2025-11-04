from typing import Any, Dict, Optional

import streamlit as st
from streamlit_folium import folium_static
from utils.map_utils import create_property_map
from utils.place_utils import get_place_emoji, categorize_places
from utils.demographic_utils import (
    get_population_growth_color,
    get_deprivation_rate_color,
    get_crime_rate_color
)
from app.components.criteria_components import render_lifestyle_criteria
from app.modules.property.utils import format_currency, value_or_placeholder


TRANSPORT_EMOJIS = {
    "walk": "🚶",
    "bus": "🚌",
    "tube": "🚇",
    "train": "🚆",
    "tram": "🚊",
    "bike": "🚲",
    "car": "🚗",
    "overground": "🚈",
    "dlr": "🚈",
}


def _map_status(color_code: str) -> str:
    mapping = {
        "normal": "positive",
        "inverse": "negative",
        "off": "neutral",
    }
    return mapping.get(color_code, "neutral")


def _render_demographic_metric(label: str, value: str, status: str, help_text: Optional[str] = None) -> None:
    st.markdown(
        """
        <style>
        .demographic-metric {
            background-color: #f0f2f6;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 8px;
        }
        .demographic-metric .label {
            color: #6c757d;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .demographic-metric .value {
            font-size: 1.2rem;
            font-weight: 600;
        }
        .demographic-metric.positive {
            border-left: 4px solid #00acb5;
        }
        .demographic-metric.negative {
            border-left: 4px solid #d9534f;
        }
        .demographic-metric.neutral {
            border-left: 4px solid #adb5bd;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    help_suffix = f"<div class='help-text'>{help_text}</div>" if help_text else ""
    st.markdown(
        f"""
        <div class="demographic-metric {status}">
            <div class="label">{label}</div>
            <div class="value">{value}</div>
            {help_suffix}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _normalize_journey_data(property_details: Dict[str, Any]) -> Dict[str, Any]:
    journey = property_details.get("journey") or {}
    if isinstance(journey, dict) and "journey" in journey and isinstance(journey["journey"], dict):
        return journey["journey"]
    return journey if isinstance(journey, dict) else {}


def _render_mode_breakdown(mode: str, data: Dict[str, Any]) -> None:
    emoji = TRANSPORT_EMOJIS.get(mode.lower(), "🧭")
    duration = data.get("duration")
    primary_line = f"{emoji} **{mode.title()}**"
    if duration:
        primary_line += f" · {value_or_placeholder(duration, 'Unknown')} min"
    st.markdown(primary_line)

    legs = data.get("legs")
    if isinstance(legs, list):
        for leg in legs:
            route = leg.get("route")
            origin = leg.get("from")
            destination = leg.get("to")
            segment = " → ".join(filter(None, [origin, destination]))
            detail = segment if segment else "Segment"
            if route not in (None, ""):
                detail = f"Route {route}: {detail}"
            st.markdown(f"&nbsp;&nbsp;↳ {detail}", unsafe_allow_html=True)


def render_transport_info(property_details: Dict[str, Any], user_submission: Optional[Dict[str, Any]]) -> None:
    """Render transport information in a bordered container."""
    journey_data = _normalize_journey_data(property_details)
    total = journey_data.get("total") or journey_data.get("duration")
    modes = journey_data.get("modes") if isinstance(journey_data.get("modes"), dict) else {}

    workplace = None
    if user_submission and isinstance(user_submission, dict):
        content = user_submission.get("content") or {}
        workplace = content.get("workplace_location")

    with st.container(border=True):
        st.markdown("### 🚉 Transport Information")

        if workplace or total is not None or modes:
            header = workplace or "Commute to work"
            if total is not None:
                header += f" · {value_or_placeholder(total, 'Ask agent')} min"
            st.markdown(f"**{header}**")

            for mode, data in modes.items():
                if isinstance(data, dict):
                    _render_mode_breakdown(mode, data)

        # Nearest stations
        stations = property_details.get("stations")
        if stations:
            st.markdown("**Nearest stations**")
            for station in stations:
                name = station.get("station") or station.get("name")
                distance = station.get("distance")
                if name:
                    suffix = f" ({distance} miles)" if distance else ""
                    st.markdown(f"- {name}{suffix}")

def render_neighborhood_statistics(property_details):
    """Render neighborhood statistics with color-coded metrics."""
    st.markdown("### 📊 Neighborhood Statistics")
    with st.container(border=True):
        neighborhood_information = property_details.get("neighborhood_information")
        neighborhood_information = property_details.get("neighborhood_info") if not neighborhood_information else neighborhood_information
        demographic_stats = neighborhood_information.get("demographics", {}) if neighborhood_information else {}

        columns = st.columns(5)

        if demographic_stats.get('crime_rate') is not None:
            crime_rate = str(demographic_stats['crime_rate'])
            status = _map_status(get_crime_rate_color(crime_rate))
            with columns[0]:
                _render_demographic_metric("Crime rate", crime_rate, status, "Crimes per 1,000 people")

        if demographic_stats.get('deprivation_rate') is not None:
            deprivation_rate = str(demographic_stats['deprivation_rate'])
            status = _map_status(get_deprivation_rate_color(deprivation_rate))
            with columns[1]:
                _render_demographic_metric(
                    "Deprivation rate",
                    deprivation_rate,
                    status,
                    "Households facing deprivation in ≥1 dimension",
                )

        if demographic_stats.get('avg_income') is not None:
            avg_income = demographic_stats['avg_income']
            formatted_income = format_currency(avg_income)
            with columns[2]:
                _render_demographic_metric("Avg. household income", formatted_income, "neutral")

        if demographic_stats.get('10_year_population_growth') is not None:
            growth = str(demographic_stats['10_year_population_growth'])
            status = _map_status(get_population_growth_color(growth))
            with columns[3]:
                _render_demographic_metric("10-year population growth", growth, status)

        if demographic_stats.get('degree_rate') is not None:
            degree_rate = str(demographic_stats['degree_rate'])
            with columns[4]:
                _render_demographic_metric("Degree rate", degree_rate, "neutral", "Households with higher education")

        if neighborhood_information:
            bedrooms = property_details.get('num_bedrooms')
            asking_price = neighborhood_information.get('asking_price')
            asking_rent = neighborhood_information.get('asking_rent')
            if asking_price is not None:
                st.markdown(
                    f"**Avg. asking price for {bedrooms} bedrooms:** {format_currency(asking_price)}"
                )
            elif asking_rent is not None:
                st.markdown(
                    f"**Avg. asking rent for {bedrooms} bedrooms:** {format_currency(asking_rent)} pcm"
                )


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

def render_location_tab(property_details, user_submission=None):
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
        render_transport_info(property_details, user_submission)

    # Render lifestyle criteria first (neighborhood-related)

    with st.container():
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
