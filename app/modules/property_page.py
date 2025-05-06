import streamlit as st
from connection.firestore import FireStore
from app.modules.chat import show_chat_interface
import base64
import json
import folium
from streamlit_folium import folium_static

def show_property_page(firestore: FireStore):
    """Show the property detail page."""
    # Get property ID from query parameters
    property_id = st.query_params.get("property_id", "")
    if not property_id:
        st.error("No property ID provided")
        return

    # Try to get property details from session state first
    property_details = None
    if hasattr(st.session_state, 'property_shortlist'):
        property_details = st.session_state.property_shortlist.get(int(property_id))
    
    # If not in session state, fetch from Firestore
    if not property_details:
        print(f"Property {property_id} not found in session state, fetching from Firestore")
        property_details = firestore.get_property_by_id(property_id)
        if not property_details:
            st.error("Property not found")
            return
        print(f"Fetched from Firestore, available fields: {list(property_details.keys())}")

    # Back to dashboard button
    if st.button("← Back to Dashboard", key="back_to_dashboard_from_property"):
        st.query_params.clear()
        st.rerun()

    # Property header
    st.title(property_details['address'])
    st.markdown(f"### £{property_details['price']:,} | {property_details['num_bedrooms']} bedrooms")

    # Display images in a 2x4 grid
    if property_details.get('compressed_images'):
        st.markdown("### Property Images")
        # Create 2 rows of 4 columns
        for row in range(2):
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                if idx < len(property_details['compressed_images']):
                    try:
                        # Decode image if not already in session state
                        if f"img_{property_id}_{idx}" not in st.session_state:
                            decoded_image = base64.b64decode(property_details['compressed_images'][idx])
                            st.session_state[f"img_{property_id}_{idx}"] = decoded_image
                        
                        with cols[col]:
                            st.image(
                                st.session_state[f"img_{property_id}_{idx}"],
                                use_column_width=True
                            )
                    except Exception as e:
                        print(f"Error displaying image {idx} for property {property_id}: {str(e)}")

    # Property details in tabs
    tab1, tab2, tab3 = st.tabs(["Property Details", "Location", "Chat with AI"])

    with tab1:
        st.markdown("### Property Information")
        match_criteria = property_details.get("match_output", {})
        match_criteria_additional = property_details.get("matched_criteria", {})
        match_criteria.update({criteria: True for criteria in match_criteria_additional})
        for key, value in match_criteria.items():
            if isinstance(value, bool) and value:
                st.markdown(f"<h4 style='font-size: 20px; margin: 10px 0;'>✅ {key.replace('_', ' ').capitalize()}</h4>", unsafe_allow_html=True)

        # Display property details
        st.markdown("#### Property Details")
        col1, col2 = st.columns(2)
        with col1:
            if property_details.get('tenure_type'):
                st.markdown(f"**Tenure Type:** {property_details['tenure_type']}")
                if property_details['tenure_type'] != "FREEHOLD":
                    if property_details.get('ground_rent'):
                        st.markdown(f"**Ground Rent:** £{property_details['ground_rent']:,}")
                    if property_details.get('service_charge'):
                        st.markdown(f"**Service Charge:** £{property_details['service_charge']:,}")
                    if property_details.get('length_of_lease'):
                        st.markdown(f"**Lease Length:** {property_details['length_of_lease']} years")

        with col2:
            if property_details.get('deprivation') and property_details["deprivation"] > 0:
                st.markdown(f"**Area deprivation:** {property_details.get('deprivation')}%")
                if property_details['deprivation'] < 20:
                    st.markdown("⭐ Relatively wealthy area")

        # Display floorplan and EPC side by side in bordered boxes
        st.markdown("### Property Documents")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Floorplan")
            with st.container():
                st.markdown('<div class="bordered-box">', unsafe_allow_html=True)
                if property_details.get('floorplans') and isinstance(property_details["floorplans"], list):
                    floorplan = property_details["floorplans"][0]  # Get the first floorplan
                    if floorplan.get('url'):
                        st.image(floorplan['url'], caption=floorplan.get('caption', 'Floorplan'), width=300)
                        if floorplan.get('url'):
                            st.markdown(f"[View Full Size Floorplan]({floorplan['url']})")
                else:
                    st.info("Ask Agent for floorplan")
                st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("#### Energy Performance Certificate")
            with st.container():
                st.markdown('<div class="bordered-box">', unsafe_allow_html=True)
                if property_details.get('epc'):
                    try:
                        # Handle both URL and base64 encoded images
                        if isinstance(property_details['epc'], str):
                            if property_details['epc'].startswith('data:image'):
                                # Handle base64 encoded image
                                st.image(property_details['epc'], caption="EPC Rating", width=300)
                            else:
                                # Handle URL
                                st.image(property_details['epc'], caption="EPC Rating", width=300)
                        else:
                            st.error("Invalid EPC image format")
                    except Exception as e:
                        st.error(f"Error displaying EPC: {str(e)}")
                        print(f"EPC display error: {str(e)}")
                else:
                    st.info("EPC not available")
                st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown("### Location Information")
        
        # Create map centered on property location or central London
        latitude = property_details.get('latitude')  # Default to central London
        longitude = property_details.get('longitude')  # Default to central London
        if not (isinstance(latitude, float) and isinstance(longitude, float)):
            latitude, longitude = 51.5074, -0.1278
        # Create the map
        m = folium.Map(location=[latitude, longitude], zoom_start=15)
        
        # Add marker for the property
        folium.Marker(
            [latitude, longitude],
            popup=property_details['address'],
            icon=folium.Icon(color='red', icon='home', prefix='fa')
        ).add_to(m)
        
        # Display the map
        folium_static(m, width=700, height=400)
        
        # Display commute time and transport information
        st.markdown("### Transport Information")
        col1, col2 = st.columns(2)
        
        with col1:
            if property_details.get("journey") and property_details["journey"].get("duration"):
                st.markdown(f"**Commute to work:** {property_details['journey'].get('duration')} min")
        
        with col2:
            if "stations" in property_details:
                st.markdown("**Nearest Stations:**")
                for station in property_details["stations"]:
                    st.markdown(f"- {station['station']} ({station['distance']} miles)")

        # Display nearby places
        st.markdown("### Places of Interest")
        with st.expander("View places within 1km"):
            for place in property_details.get("places_of_interest", []):
                if place.get("rating"):
                    st.markdown(f"- {place['name']} (⭐ {place['rating']})")
                else:
                    st.markdown(f"- {place['name']}")

    with tab3:
        show_chat_interface() 