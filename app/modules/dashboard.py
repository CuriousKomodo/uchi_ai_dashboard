import streamlit as st

from connection.firestore import FireStore
from custom_exceptions import NoUserFound
from utils.draft import draft_enquiry
from utils.filter import sort_by_chosen_option
from app.components.preferences_view import show_preferences_section

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

    # Fetch user's submission data first
    with st.spinner(f'Hello {st.session_state.first_name}. Loading your preferences...'):
        submissions = firestore.get_submissions_by_user_id(st.session_state.user_id)
        if submissions:
            # Store the most recent submission in session state
            st.session_state.user_submission = submissions[-1]  # Get the most recent submission
        else:
            st.session_state.user_submission = None

    # Display user preferences if available
    if st.session_state.user_submission:
        show_preferences_section(st.session_state.user_submission)

    # Fetch properties from Firestore
    with st.spinner(f'Hello {st.session_state.first_name}. Loading properties for you...'):
        shortlist = firestore.get_shortlists_by_user_id(st.session_state.user_id)
        # TODO: replace me with the actual flow
        # st.header("Feature Properties")
        # st.subheader("3 bedrooms in Dollis Hill - 450k")
        # video_url = "https://www.youtube.com/watch?v=Y7OFw2bcYNY"
        # st.video(video_url)
        # Store the complete shortlist in session state
        st.session_state.property_shortlist = {}
        for prop in shortlist:
            # Ensure we have all the required fields
            property_data = {
                'property_id': prop['property_id'],
                'postcode': prop.get('postcode'),
                'address': prop['address'],
                'price': prop['price'],
                'num_bedrooms': prop['num_bedrooms'],
                'compressed_images': prop.get('compressed_images', []),
                'floorplan': prop.get('floorplan', []),
                'latitude': prop.get('latitude'),
                'longitude': prop.get('longitude'),
                'stations': prop.get('stations', []),
                'match_output': prop.get('match_output', {}),
                'matched_criteria': prop.get('matched_criteria', {}),
                'matched_lifestyle_criteria': prop.get('matched_lifestyle_criteria', {}),
                "prop_property_criteria_matched": prop.get('prop_property_criteria_matched', 0),
                'journey': prop.get('journey', {}),
                'deprivation': prop.get('deprivation'),
                'places_of_interest': prop.get('places_of_interest', []),
                "epc": prop.get("epc"),
                "features": prop.get("features", []),
                "council_tax_band": prop.get("council_tax_band", []),
                # only applicable for flats
                'ground_rent': prop.get('groundRent'),
                'tenure_type': prop.get('tenure_type'),
                'service_charge': prop.get('annualServiceCharge'),
                'length_of_lease': prop.get('lengthOfLease'),

                # AI extracted
                "neighborhood_info": prop.get('neighborhood_info', {}),
                "description_analysis": prop.get('description_analysis', {}),
                "image_analysis": prop.get('image_analysis', {}),
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

        # Add custom CSS for property cards
        st.markdown("""
            <style>
            .property-card {
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 20px;
                background-color: white;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                transition: transform 0.2s;
            }
            .property-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            }
            .property-image {
                width: 100%;
                height: 200px;
                object-fit: cover;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            .property-title {
                font-size: 1.2em;
                font-weight: bold;
                margin: 10px 0;
                color: #1f1f1f;
            }
            .property-price {
                font-size: 1.1em;
                color: #2e7d32;
                font-weight: bold;
                margin: 5px 0;
            }
            .property-details {
                font-size: 0.9em;
                color: #666;
                margin: 5px 0;
            }
            .criteria-tag {
                display: inline-block;
                background-color: #e3f2fd;
                color: #1976d2;
                padding: 4px 8px;
                border-radius: 4px;
                margin: 2px;
                font-size: 0.8em;
            }
            .view-details-btn {
                width: 100%;
                margin-top: 15px;
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
                font-size: 1.1em;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                box-shadow: 0 2px 4px rgba(25, 118, 210, 0.3);
            }
            .view-details-btn:hover {
                background-color: #1565c0;
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(25, 118, 210, 0.4);
            }
            .view-details-btn:active {
                transform: translateY(0);
                box-shadow: 0 2px 4px rgba(25, 118, 210, 0.3);
            }
            </style>
        """, unsafe_allow_html=True)

        # Create a grid of property cards
        for i in range(0, len(shortlist), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(shortlist):
                    prop = shortlist[i + j]
                    with cols[j]:
                        # Create property card
                        #st.markdown('<div class="property-card">', unsafe_allow_html=True)
                        with st.container(border=True):
                            # Display property image
                            if prop.get('compressed_images'):
                                try:
                                    # Decode the first image if not already decoded
                                    if prop['property_id'] not in st.session_state.decoded_images:

                                        if isinstance(prop['compressed_images'][0], str):
                                            decoded_image = base64.b64decode(prop['compressed_images'][0])  # FIXME: backward compatible
                                        elif isinstance(prop['compressed_images'][0], dict):
                                            decoded_image = base64.b64decode(prop['compressed_images'][0]["base64"])

                                        st.session_state.decoded_images[prop['property_id']] = [decoded_image]

                                    st.image(
                                        st.session_state.decoded_images[prop['property_id']][0],
                                        use_column_width=True
                                    )
                                except Exception as e:
                                    print(f"Error displaying image for property {prop['property_id']}: {str(e)}")
                                    st.write("No image available")

                            # Property title and price
                            st.markdown(f'<div class="property-title">{prop["address"]}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="property-price">£{prop["price"]:,}</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="property-details">{prop["num_bedrooms"]} bedrooms</div>', unsafe_allow_html=True)

                            # Display matched criteria
                            match_criteria = prop.get("match_output", {})
                            match_criteria_additional = prop.get("matched_criteria", {})
                            match_criteria.update({criteria: True for criteria in match_criteria_additional})

                            criteria_html = '<div style="margin: 10px 0;">'
                            for key, value in match_criteria.items():
                                if isinstance(value, bool) and value:
                                    criteria_html += f'<span class="criteria-tag">{key.replace("_", " ").capitalize()}</span>'
                            criteria_html += '</div>'
                            st.markdown(criteria_html, unsafe_allow_html=True)

                            # View Details button
                            if st.button(
                                    "View Details",
                                    key=f"detail_{prop['property_id']}",
                                    use_container_width=True,
                                    type="primary"
                            ):
                                st.query_params.update(property_id=prop['property_id'])
                                st.rerun()
                        
                        #st.markdown('</div>', unsafe_allow_html=True)