import streamlit as st
from connection.firestore import FireStore
from custom_exceptions import NoUserFound
from utils.draft import draft_enquiry
from utils.filter import sort_by_chosen_option

import base64
import json

def on_draft_enquiry(
        property_id: str,
        property_details: dict,
        customer_name: str,
        customer_intent: str = ""
):
    expander_key = f"expander_{property_id}"
    message = draft_enquiry(
        property_details=property_details,
        customer_name=customer_name,
        customer_intent=customer_intent,
    )

    # store your draft and expand flag in session_state
    st.session_state[f"draft_msg_{property_id}"] = message
    st.session_state[expander_key] = True

def login(firestore: FireStore):
    """Handle user login."""
    st.title("Log into Uchi Dashboard")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user_details = firestore.fetch_user_details_by_email(email)
            if user_details.get("password") == password:
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.user_id = user_details.get("user_id")
                st.session_state.first_name = user_details.get("first_name")
                st.rerun()
            else:
                st.error("Invalid password")
        except NoUserFound:
            st.error("Email is not found. Please feel free to register.")

def show_dashboard(firestore: FireStore):
    """Show the main dashboard."""
    # Login check
    if not st.session_state.authenticated:
        login(firestore)
        return

    # Initialize session state for image caching
    if "decoded_images" not in st.session_state:
        st.session_state.decoded_images = {}

    # Fetch properties from Firestore
    with st.spinner(f'Hello {st.session_state.first_name}. Loading properties for you...'):
        shortlist = firestore.get_shortlists_by_user_id(st.session_state.user_id)
        
        # Store the complete shortlist in session state
        st.session_state.property_shortlist = {}
        for prop in shortlist:
            # Ensure we have all the required fields
            property_data = {
                'property_id': prop['property_id'],
                'address': prop['address'],
                'price': prop['price'],
                'num_bedrooms': prop['num_bedrooms'],
                'compressed_images': prop.get('compressed_images', []),
                'floorplans': prop.get('floorplans', []),
                'latitude': prop.get('latitude'),
                'longitude': prop.get('longitude'),
                'stations': prop.get('stations', []),
                'match_output': prop.get('match_output', {}),
                'matched_criteria': prop.get('matched_criteria', {}),
                'journey': prop.get('journey', {}),
                'deprivation': prop.get('deprivation'),
                'places_of_interest': prop.get('places_of_interest', []),
                # only applicable for flats
                'ground_rent': prop.get('groundRent'),
                'tenure_type': prop.get('tenureType'),
                'service_charge': prop.get('annualServiceCharge'),
                'length_of_lease': prop.get('lengthOfLease'),
            }
            st.session_state.property_shortlist[prop['property_id']] = property_data

    if shortlist:
        sort_by = st.selectbox(
            "Sort by",
            options=["Price: Low to High",
                     "Price: High to Low",
                     "Bedrooms: Most to Fewest",
                     "Commute time to work: Shortest to Longest",
                     "Criteria Match: Most to Least"
                     ],
            placeholder="Price: Low to High",
            key="user_sort_order"
        )
        if not sort_by:
            sort_by_chosen_option("Price: Low to High", shortlist)
        sort_by_chosen_option(st.session_state.user_sort_order, shortlist)

        for prop in shortlist:
            st.markdown("---")
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    # Display property image in a smaller container
                    if prop.get('compressed_images'):
                        try:
                            # Decode the first image if not already decoded
                            if prop['property_id'] not in st.session_state.decoded_images:
                                decoded_image = base64.b64decode(prop['compressed_images'][0])
                                st.session_state.decoded_images[prop['property_id']] = [decoded_image]
                            
                            # Create a container for the image with max width
                            with st.container():
                                st.image(
                                    st.session_state.decoded_images[prop['property_id']][0],
                                    width=300  # Set a fixed width for the image
                                )
                        except Exception as e:
                            print(f"Error displaying image for property {prop['property_id']}: {str(e)}")
                            st.write("No image available")
                    
                    # Display property details
                    st.markdown(f"<h3>{prop['address']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<h4>{prop['num_bedrooms']} bedrooms - £{prop['price']:,}</h4>", unsafe_allow_html=True)
                    
                    # Display matched criteria
                    match_criteria = prop.get("match_output", {})
                    match_criteria_additional = prop.get("matched_criteria", {})
                    match_criteria.update({criteria: True for criteria in match_criteria_additional})
                    criteria_string = ""
                    for key, value in match_criteria.items():
                        if isinstance(value, bool) and value:
                            criteria_string += f" {key.replace('_', ' ').capitalize()} ✅  "
                    st.markdown(criteria_string, unsafe_allow_html=True)
                
                with col2:
                    # Detail button
                    if st.button("View Details", key=f"detail_{prop['property_id']}"):
                        st.query_params.update(property_id=prop['property_id'])
                        st.rerun()