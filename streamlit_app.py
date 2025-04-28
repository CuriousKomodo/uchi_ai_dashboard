import base64
import json
import time
from typing import Dict, List, Optional

import streamlit as st

from connection.firestore import FireStore
from custom_exceptions import NoUserFound
from utils.draft import draft_enquiry
from utils.filter import sort_by_chosen_option
from utils.image_gallery_manager import ImageGalleryManager

# Constants for cache management
MAX_CACHED_PROPERTIES = 10  # Maximum number of properties to cache
CACHE_CLEANUP_THRESHOLD = 100  # Cleanup when this many properties are cached

firestore = FireStore(credential_info=st.secrets["firestore_credentials"])
st.set_page_config(page_title="AI-Powered Real Estate Assistant", layout="wide")

# Initialize session state for authentication and cache management
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "last_access_time" not in st.session_state:
    st.session_state.last_access_time = {}
if "user_sort_order" not in st.session_state:
    st.session_state.user_sort_order = ""
if "chat_flag" not in st.session_state:
    st.session_state.chat_flag = None

def cleanup_old_caches():
    """Clean up old caches when we exceed the threshold."""
    if len(st.session_state.decoded_images) > CACHE_CLEANUP_THRESHOLD:
        # Sort properties by last access time
        sorted_properties = sorted(
            st.session_state.last_access_time.items(),
            key=lambda x: x[1]
        )
        
        # Remove oldest caches until we're under the limit
        for property_id, _ in sorted_properties:
            if len(st.session_state.decoded_images) <= MAX_CACHED_PROPERTIES:
                break
            if property_id in st.session_state.decoded_images:
                del st.session_state.decoded_images[property_id]
                del st.session_state.image_indices[property_id]
                del st.session_state.last_access_time[property_id]

def update_cache_access_time(property_id: str):
    """Update the last access time for a property's cache."""
    st.session_state.last_access_time[property_id] = time.time()

def on_draft_enquiry(
        property_id: str,
        property_details: Dict,
        customer_name: str,
        customer_intent: Optional[str] = ""
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


def load_main_dashboard():

    st.title("🏡 Uchi: AI-Powered Real Estate Assistant")

    # Fetch properties from Firestore
    st.subheader("🏠 Recommended Properties")

    # Show loading indicator while fetching data
    with st.spinner(f'Hello {st.session_state.first_name}. Loading properties for you...'):
        shortlist = firestore.get_shortlists_by_user_id(st.session_state.user_id)

    if shortlist:
        sort_by = st.selectbox(
            "Sort by",
            options=["Price: Low to High",
                     "Price: High to Low",
                     "Bedrooms: Most to Fewest",
                     "Commute time to work: Shortest to Longest",
                     "Criteria Match: Most to Least"
                     ],
            key="user_sort_order"
        )
        sort_by_chosen_option(sort_by, shortlist)

        # Initialize image gallery manager and pre-decode all images
        gallery_manager = ImageGalleryManager()
        gallery_manager.pre_decode_images(shortlist)

        for prop in shortlist:
            st.markdown("---")  # Adds a separator between properties
            with st.container():
                col1, col2, col3, col4 = st.columns([5, 1, 2, 2])
                with col1:
                    st.markdown(f"<h3>{prop['address']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<h4>{prop['num_bedrooms']} bedrooms - £{prop['price']}</h4>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                with col2:
                    if st.button(f"❤️ Save", key=f"save {prop['property_id']}"):
                        st.success("Property saved!")

                with col3:
                    # Unique key for this property's enquiry
                    enquiry_key = f"enquire_{prop['property_id']}"

                    # If the button is clicked, store the draft and open the expander
                    if st.button(
                            "️✉️ Draft enquiry",
                            key=enquiry_key,
                            on_click=on_draft_enquiry,
                            args=(prop['property_id'], prop, st.session_state.first_name, "general enquiry")
                    ):
                        pass

                with col4:
                    if st.session_state.get(f"draft_msg_{prop['property_id']}", False):
                        with st.popover("📝Review your draft"):
                            st.markdown(
                                f"<h5>Subject: enquiring about property at {prop['address']}</h3>",
                                unsafe_allow_html=True
                            )
                            st.text_area(
                                f"Feel free to edit the content.",
                                value=st.session_state.get(f"draft_msg_{prop['property_id']}"),
                                height=300,
                                key=f"textarea_{prop['property_id']}"
                            )
            with st.container():
                col1, col2 = st.columns([3, 5])
                # Display image gallery on the left
                with col1:
                    gallery_manager.display_image_gallery(prop)

                    col11, col12, col13 = st.columns([1,1,1])
                    with col11:
                        st.link_button("View original", url=f"https://www.rightmove.co.uk/properties/{prop['property_id']}")
                    with col12:
                        chat_url = (
                            f"{st.secrets['UCHI_LIVE_CHAT_URL']}?"
                            f"property_id={prop['property_id']}"
                        )  # will require security check in the future
                        st.link_button(
                            "🤖Ask AI",
                            url=chat_url
                        )
                    with col13:
                        if prop.get('floorplans') and isinstance(prop["floorplans"], list):
                            floorplan_url = prop["floorplans"][0].get("url")
                            st.link_button("Floorplan", url=floorplan_url)

                    if "stations" in prop:
                        st.write("**🚉 Nearest Stations:**")
                        for station in prop["stations"]:
                            st.write(f"- {station['station']} ({station['distance']} miles)")

                # Display property details on the right
                with col2:
                    st.write("<h5>🏠Matched property criteria: </h5>", unsafe_allow_html=True)
                    match_criteria = prop.get("match_output", {})
                    match_criteria_additional = prop.get("matched_criteria", {})
                    match_criteria.update({criteria: True for criteria in match_criteria_additional})
                    match_criteria_string = ""  # widgets with colors
                    for key, value in match_criteria.items():
                        if isinstance(value, bool) and value:
                            match_criteria_string += f" {key.replace('_', ' ').capitalize()} ✅  "
                    st.markdown(match_criteria_string, unsafe_allow_html=True)

                    if prop["journey"] and prop["journey"].get("duration"):
                        st.markdown(
                            f"<h6>🚗Estimated commute to work: {prop['journey'].get('duration')} min </h6>",
                            unsafe_allow_html=True
                        )
                    if prop.get('deprivation') and prop["deprivation"] > 0:
                        st.markdown(f"<h6>% households with any deprivation: {prop.get('deprivation')}% <h6>",
                                    unsafe_allow_html=True)
                        if prop['deprivation'] < 20:
                            st.markdown(
                                "⭐Relatively wealthy area, i.e. fewer than 1 in 5 residents are income‑deprived.")

                    with st.expander("🏞️🧘Places within 1km which might be relevant", expanded=False):
                        st.markdown(
                            "<div style='min-width: 500px;'>", unsafe_allow_html=True
                        )
                        for place in prop.get("places_of_interest", []):
                            if place.get("rating"):
                                st.write(f"- {place['name']} (⭐ {place['rating']})")
                            else:
                                st.write(f"- {place['name']} ")
                        st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.write("No properties found in your shortlist.")

    # Sidebar for user account settings
    st.sidebar.header("⚙️ Account Settings")
    st.sidebar.link_button("Create a new submission", url="https://uchi-survey.streamlit.app/")
    st.sidebar.link_button("Contact us",  url="www.uchiai.co.uk")

# Login Function
def login():
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

# Logout Function
def logout():
    st.session_state.authenticated = False
    st.session_state.email = None
    st.session_state.user_id = None
    st.session_state.first_name = None
    st.rerun()

# App Content
if not st.session_state.authenticated:
    login()
else:
    load_main_dashboard()
    st.sidebar.button("Logout", on_click=logout)

