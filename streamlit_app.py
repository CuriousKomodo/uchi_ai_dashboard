import base64
import json

import streamlit as st

from connection.firestore import FireStore
from custom_exceptions import NoUserFound
from utils import read_json


firestore = FireStore(credential_info=st.secrets["firestore_credentials"])
st.set_page_config(page_title="AI-Powered Real Estate Assistant", layout="wide")
# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False


def load_main_dashboard():
    st.title("🏡 Uchi: AI-Powered Real Estate Assistant")

    # Fetch properties from Firestore
    st.subheader("🏠 Recommended Properties")

    # Show loading indicator while fetching data
    with st.spinner('Loading properties...'):
        shortlist = firestore.get_shortlists_by_user_id(st.session_state.user_id)

    if shortlist:
        # Initialize session state for image indices if not exists
        if "image_indices" not in st.session_state:
            st.session_state.image_indices = {}

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
                # Display a single image on the left
                with col1:
                    if prop.get("compressed_images"):
                        property_id = prop['property_id']
                        if property_id not in st.session_state.image_indices:
                            st.session_state.image_indices[property_id] = 0

                        img_index = st.session_state.image_indices[property_id]
                        
                        # Lazy load image
                        try:
                            img_data = base64.b64decode(prop["compressed_images"][img_index])
                            st.image(img_data, use_column_width=True)
                        except Exception as e:
                            st.error(f"Error loading image: {str(e)}")

                        col_img1, col_img2, col_img3 = st.columns([1,1,1])
                        with col_img1:
                            if st.button("⬅️prev", key=f" Previous {property_id}") and img_index > 0:
                                st.session_state.image_indices[property_id] -= 1
                                st.rerun()
                        with col_img3:
                            if st.button("next ➡️", key=f"️ Next {property_id}") and img_index < len(
                                    prop["compressed_images"]) - 1:
                                st.session_state.image_indices[property_id] += 1
                                st.rerun()
                        with col_img2:
                            pass

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

