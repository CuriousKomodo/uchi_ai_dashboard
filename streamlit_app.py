import base64
import json
import time
from typing import Dict, List

import streamlit as st

from connection.firestore import FireStore
from custom_exceptions import NoUserFound
from utils.image_gallery_utils import ImageGalleryManager

# Constants for cache management
MAX_CACHED_PROPERTIES = 10  # Maximum number of properties to cache
CACHE_CLEANUP_THRESHOLD = 15  # Cleanup when this many properties are cached

firestore = FireStore(credential_info=st.secrets["firestore_credentials"])
st.set_page_config(page_title="AI-Powered Real Estate Assistant", layout="wide")

# Initialize session state for authentication and cache management
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "last_access_time" not in st.session_state:
    st.session_state.last_access_time = {}

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

def load_main_dashboard():
    st.title("🏡 Uchi: AI-Powered Real Estate Assistant")

    # Fetch properties from Firestore
    st.subheader("🏠 Recommended Properties")

    # Show loading indicator while fetching data
    with st.spinner('Loading properties...'):
        shortlist = firestore.get_shortlists_by_user_id(st.session_state.user_id)

    if shortlist:
        # Initialize image gallery manager
        gallery_manager = ImageGalleryManager()

        for prop in shortlist:
            st.markdown("---")  # Adds a separator between properties
            with st.container():
                col1, col2 = st.columns([5, 1])
                with col1:
                    st.markdown(f"<h3>{prop['address']} - £{prop['price']}</h3>", unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                with col2:
                    if st.button(f"❤️ Save", key=f"save {prop['property_id']}"):
                        st.success("Property saved!")
            
            with st.container():
                col1, col2 = st.columns([1, 2])
                # Display image gallery on the left
                with col1:
                    gallery_manager.display_image_gallery(prop)

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

                    st.markdown("<h6>🚗Estimated commute to Liverpool Street = 50min</h6>", unsafe_allow_html=True)

                    with st.expander("🕵️Neighborhood intelligence", expanded=False):
                        st.markdown(
                            "<div style='min-width: 500px;'>", unsafe_allow_html=True
                        )
                        if prop.get('deprivation'):
                            st.markdown(f"<h6>% households with any deprivation: {prop.get('deprivation')}% <h6>", unsafe_allow_html=True)

                        st.write("🏞️🧘Interesting places to visit within 1km")
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
    st.rerun()

# App Content
if not st.session_state.authenticated:
    login()
else:
    load_main_dashboard()
    st.sidebar.button("Logout", on_click=logout)

