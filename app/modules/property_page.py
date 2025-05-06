import base64
import json
import streamlit as st
import folium
from streamlit_folium import folium_static
from connection.firestore import FireStore
from app.modules.chat import show_chat_interface
from app.utils.location_utils import extract_prefix_postcode, calculate_distance, get_nearby_schools

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
        st.markdown("#### Matched Criteria")
        match_criteria = property_details.get("match_output", {})
        match_criteria_additional = property_details.get("matched_criteria", {})
        match_criteria.update({criteria: True for criteria in match_criteria_additional})
        
        # Create a container for matched criteria with custom styling
        st.markdown("""
            <style>
            .criteria-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 10px;
                margin: 15px 0;
            }
            .criteria-item {
                padding: 12px 15px;
                border-radius: 8px;
                font-size: 16px;
                display: flex;
                align-items: center;
            }
            .criteria-item::before {
                content: "✓";
                font-weight: bold;
                margin-right: 10px;
                font-size: 18px;
            }
            .criteria-blue {
                background-color: #e6f3ff;
                border: 1px solid #b3d9ff;
            }
            .criteria-blue::before {
                color: #0066cc;
            }
            .criteria-pink {
                background-color: #ffe6f3;
                border: 1px solid #ffb3d9;
            }
            .criteria-pink::before {
                color: #cc0066;
            }
            .criteria-green {
                background-color: #e6ffe6;
                border: 1px solid #b3ffb3;
            }
            .criteria-green::before {
                color: #006600;
            }
            .criteria-orange {
                background-color: #fff2e6;
                border: 1px solid #ffd9b3;
            }
            .criteria-orange::before {
                color: #cc6600;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Create the criteria grid
        criteria_html = '<div class="criteria-grid">'
        colors = ['blue', 'pink', 'green', 'orange']
        for idx, (key, value) in enumerate(match_criteria.items()):
            if isinstance(value, bool) and value:
                color_class = f'criteria-{colors[idx % len(colors)]}'
                criteria_html += f'<div class="criteria-item {color_class}">{key.replace("_", " ").capitalize()}</div>'
        criteria_html += '</div>'
        
        st.markdown(criteria_html, unsafe_allow_html=True)

        # Display property details
        st.markdown("#### Property Details")
        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                if property_details.get('tenure_type'):
                    st.markdown(f"**Tenure Type:** {property_details['tenure_type']}")
                    if property_details.get("council_tax_band"):
                        st.markdown(f"**Council Tax Band:** {property_details['council_tax_band']}")

                    if property_details['tenure_type'] != "FREEHOLD":
                        if property_details.get('ground_rent'):
                            st.markdown(f"**Ground Rent:** {property_details['ground_rent']}")
                        else:
                            st.markdown(f"**Ground Rent:** Ask Agent")
                        if property_details.get('service_charge'):
                            st.markdown(f"**Service Charge:** {property_details['service_charge']}")
                        else:
                            st.markdown(f"**Service Charge:** Ask Agent")
                        if property_details.get('length_of_lease'):
                            st.markdown(f"**Lease Length:** {property_details['length_of_lease']}")
                        else:
                            st.markdown(f"**Lease Length:** Ask Agent")


        # Display features in a nice grid layout
        if property_details.get('features'):
            st.markdown("#### Key Features")
            st.markdown("""
                <style>
                .feature-grid {
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 10px;
                    margin: 15px 0;
                }
                .feature-item {
                    background-color: #f0f2f6;
                    padding: 10px 15px;
                    border-radius: 5px;
                    font-size: 16px;
                    display: flex;
                    align-items: center;
                }
                .feature-item::before {
                    content: "✓";
                    color: #00acb5;
                    font-weight: bold;
                    margin-right: 8px;
                }
                </style>
            """, unsafe_allow_html=True)
            
            # Create the feature grid
            features_html = '<div class="feature-grid">'
            for feature in property_details['features']:
                features_html += f'<div class="feature-item">{feature}</div>'
            features_html += '</div>'
            
            st.markdown(features_html, unsafe_allow_html=True)

        # Display floorplan and EPC side by side in bordered boxes
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Floorplan")
            with st.container(border=True, height=500):
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
            with st.container(border=True, height=500):
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
        latitude = property_details.get('latitude')
        longitude = property_details.get('longitude')
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
        
        # Add nearby schools
        postcode_prefix = extract_prefix_postcode(property_details['postcode'])
        if postcode_prefix:
            nearby_schools = get_nearby_schools(postcode_prefix, latitude, longitude)
            
            for school in nearby_schools:
                # Create popup content with school details
                popup_content = f"""
                    <div style='min-width: 200px'>
                        <h4 style='margin: 0 0 5px 0'>{school['name']}</h4>
                        <p style='margin: 0 0 5px 0'>
                            <strong>Distance:</strong> {school['distance']} km<br>
                            <strong>Rating:</strong> {school.get('rating', 'N/A')}
                        </p>
                        {f"<a href='{school['url']}' target='_blank' style='color: #0066cc; text-decoration: none;'>View School Website</a>" if 'url' in school else ''}
                    </div>
                """
                
                # Add school marker
                folium.Marker(
                    [school['lat'], school['lng']],
                    popup=folium.Popup(popup_content, max_width=300),
                    icon=folium.Icon(color='blue', icon='graduation-cap', prefix='fa')
                ).add_to(m)

        # Create two columns for map and transport info
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Display the map
            folium_static(m, width=800, height=500)
        
        with col2:
            # Transport information in a bordered container
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

        # Neighborhood Statistics
        st.markdown("### 📊 Neighborhood Statistics")
        with st.container(border=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                if property_details.get('deprivation') is not None:
                    st.metric("Crime Rate", f"{property_details['deprivation']}%")
            
            with col2:
                if property_details.get('deprivation') is not None:
                    st.metric("Deprivation Rate", f"{property_details['deprivation']}%")
            
            with col3:
                st.metric("Avg. Asking Price", "Coming soon")
            
            with col4:
                st.metric("Avg. Rental Price", "Coming soon")
            
            with col5:
                st.metric("Area Growth Rate", "Coming soon")

        # Places of Interest
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

        # Display nearby schools list
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

    with tab3:
        show_chat_interface() 