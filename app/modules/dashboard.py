from typing import Any, Dict, List, Optional

import streamlit as st

from connection.firestore import FireStore
from custom_exceptions import NoUserFound
from utils.filter import sort_by_chosen_option
from app.components.preferences_view import show_preferences_section
from app.components.dashboard_styles import get_dashboard_css
from app.modules.dashboard_cards import render_property_card
from app.modules.dashboard_filters import filter_properties, render_filter_controls
from app.modules.dashboard_sort import (
    render_listing_mode_selector,
    render_refresh_button,
    render_sort_control,
)
from app.modules.dashboard_utils import (
    clear_all_caches,
    filter_shortlist_by_mode,
    get_preferred_location_label, determine_listing_mode,
)

def login(firestore: FireStore):
    """Handle user login."""
    st.title("Log into Uchi Dashboard")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user_details = firestore.fetch_user_details_by_email(email)
            st.markdown(user_details)
            if user_details.get("password", "") == password:
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.user_id = user_details.get("user_id")
                st.session_state.first_name = user_details.get("first_name")
                
                # Clear any existing caches for fresh session
                clear_all_caches()
                
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

    # Initialize session state containers
    if "decoded_images" not in st.session_state:
        st.session_state.decoded_images = {}

    if "user_submission" not in st.session_state:
        with st.spinner(f'Hello {st.session_state.first_name}. Loading your preferences...'):
            submissions = firestore.get_submissions_by_user_id(st.session_state.user_id)
            st.session_state.user_submission = submissions[-1] if submissions else None

    user_submission = st.session_state.user_submission
    if user_submission:
        with st.expander("Review your requirements", icon="📝"):
            show_preferences_section(user_submission)

    if "property_shortlist" not in st.session_state or not st.session_state.property_shortlist:
        with st.spinner(f'Hello {st.session_state.first_name}. Loading properties for you...'):
            shortlisted_properties = firestore.get_shortlists_by_user_id(st.session_state.user_id)
            st.session_state.property_shortlist = {}
            for prop in shortlisted_properties:
                if isinstance(prop.get('address'), dict):
                    address = prop['address']["displayAddress"]
                else:
                    address = prop.get('address')
                property_data = {
                    'property_id': prop['property_id'],
                    'postcode': prop.get('postcode'),
                    'address': address,
                    'price': prop.get('price'),
                    'num_bedrooms': prop.get('num_bedrooms'),
                    'num_bathrooms': prop.get('num_bathrooms'),
                    'compressed_images': prop.get('compressed_images', []),
                    'floorplan': prop.get('floorplan', []),
                    'latitude': prop.get('latitude'),
                    'longitude': prop.get('longitude'),
                    'stations': prop.get('stations', []),
                    'match_output': prop.get('match_output', {}),
                    'matched_criteria': prop.get('query_matched', []) + prop.get('matched_criteria', []),
                    'matched_lifestyle_criteria': prop.get('lifestyle_criteria_matched', {}),
                    "prop_criteria_matched": prop.get('prop_criteria_matched', 0),
                    'journey': prop.get('journey', {}),
                    'deprivation': prop.get('deprivation'),
                    'places_of_interest': prop.get('places_of_interest', []),
                    "epc": prop.get("epc"),
                    "features": prop.get("features", []),
                    "council_tax_band": prop.get("council_tax_band", []),
                    'distance_to_preferred_location': prop.get('distance_to_preferred_location'),
                    'ground_rent': prop.get('groundRent'),
                    'tenure_type': prop.get('tenure_type'),
                    'service_charge': prop.get('annualServiceCharge'),
                    'length_of_lease': prop.get('lengthOfLease'),
                    'monthly_rent': prop.get('monthly_rent'),
                    'deposit': prop.get('deposit'),
                    'let_available': prop.get('let_available'),
                    'furnish_type': prop.get('furnish_type'),
                    'minimum_tenancy_months': prop.get('minimum_tenancy_months'),
                    "draft": prop.get('draft', {}),
                    "missing_info": prop.get('missing_info', {}),
                    "neighborhood_info": prop.get('neighborhood_info', {}),
                    "description_analysis": prop.get('description_analysis', {}),
                    "image_analysis": prop.get('image_analysis', {}),
                }
                st.session_state.property_shortlist[prop['property_id']] = property_data
    shortlist = list(st.session_state.property_shortlist.values())

    if not shortlist:
        st.info("No recommended properties are available right now. Please try refreshing later.")
        render_refresh_button()
        return

    st.markdown(get_dashboard_css(), unsafe_allow_html=True)

    listing_mode = determine_listing_mode(shortlist)
    shortlist_by_mode = filter_shortlist_by_mode(shortlist, listing_mode)

    if not shortlist_by_mode:
        st.info(f"No {listing_mode} properties are available yet. Adjust filters or refresh.")
        render_refresh_button()
        return

    sort_col, refresh_col = st.columns([3, 1])
    with sort_col:
        sort_choice = render_sort_control(listing_mode)
    with refresh_col:
        render_refresh_button()

    filters = render_filter_controls(shortlist_by_mode, listing_mode, user_submission)
    filtered_properties = filter_properties(shortlist_by_mode, listing_mode, filters)

    if filters.get("within_2km"):
        preferred_location = get_preferred_location_label(user_submission)
        st.info(f"📍 Showing {len(filtered_properties)} properties within 2km of {preferred_location}")

    if not filtered_properties:
        st.warning("No properties match the current filters. Try adjusting your filters.")
        return

    sort_by_chosen_option(sort_choice, filtered_properties)

    for i in range(0, len(filtered_properties), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(filtered_properties):
                with cols[j]:
                    render_property_card(filtered_properties[i + j], listing_mode)
