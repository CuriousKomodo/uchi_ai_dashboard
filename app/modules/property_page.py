import streamlit as st
from connection.firestore import FireStore
from app.modules.chat import show_chat_interface
import base64
import json

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
        if property_details:
            print(f"Found property {property_id} in session state")
            print(f"Available fields: {list(property_details.keys())}")
    
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
        # Display matched criteria
        st.write("**Matched Criteria:**")
        match_criteria = property_details.get("match_output", {})
        match_criteria_additional = property_details.get("matched_criteria", {})
        match_criteria.update({criteria: True for criteria in match_criteria_additional})
        for key, value in match_criteria.items():
            if isinstance(value, bool) and value:
                st.markdown(f"- {key.replace('_', ' ').capitalize()} ✅")

        # Display floorplan
        st.markdown("### Floorplan")
        if property_details.get('floorplans') and isinstance(property_details["floorplans"], list):
            floorplan = property_details["floorplans"][0]  # Get the first floorplan
            if floorplan.get('thumbnailUrl'):
                st.image(floorplan['thumbnailUrl'], caption=floorplan.get('caption', 'Floorplan'))
                if floorplan.get('url'):
                    st.markdown(f"[View Full Size Floorplan]({floorplan['url']})")
        else:
            st.info("Ask Agent for floorplan")

        # Display other property details
        if property_details.get("journey") and property_details["journey"].get("duration"):
            st.markdown(f"**Commute to work:** {property_details['journey'].get('duration')} min")

        if property_details.get('deprivation') and property_details["deprivation"] > 0:
            st.markdown(f"**Area deprivation:** {property_details.get('deprivation')}%")
            if property_details['deprivation'] < 20:
                st.markdown("⭐ Relatively wealthy area")

        # Display flat-specific details if available
        if property_details.get('tenure_type'):
            st.markdown("### Flat Details")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Tenure Type:** {property_details['tenure_type']}")
                if property_details.get('ground_rent'):
                    st.markdown(f"**Ground Rent:** £{property_details['ground_rent']:,}")
            with col2:
                if property_details.get('service_charge'):
                    st.markdown(f"**Service Charge:** £{property_details['service_charge']:,}")
                if property_details.get('length_of_lease'):
                    st.markdown(f"**Lease Length:** {property_details['length_of_lease']} years")

    with tab2:
        st.markdown("### Location Information")
        # Display nearest stations
        if "stations" in property_details:
            st.write("**Nearest Stations:**")
            for station in property_details["stations"]:
                st.write(f"- {station['station']} ({station['distance']} miles)")

        # Display nearby places
        with st.expander("Places of Interest within 1km"):
            for place in property_details.get("places_of_interest", []):
                if place.get("rating"):
                    st.write(f"- {place['name']} (⭐ {place['rating']})")
                else:
                    st.write(f"- {place['name']}")

    with tab3:
        show_chat_interface() 