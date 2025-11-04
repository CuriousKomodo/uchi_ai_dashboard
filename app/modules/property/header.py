from typing import Any, Dict

import streamlit as st

from utils.draft import draft_enquiry
from app.modules.property.utils import (
    determine_property_mode,
    format_price,
    format_rent,
    value_or_placeholder,
)


def _render_subtitle(property_details: Dict[str, Any], mode: str) -> None:
    """Render the property subtitle based on mode."""
    bedrooms = value_or_placeholder(property_details.get("num_bedrooms"), "Unknown beds")

    if mode == "rental":
        rent = format_rent(property_details.get("monthly_rent"))
        furnishing = value_or_placeholder(property_details.get("furnish_type"), "Unknown furnishing")
        st.markdown(f"### {rent} | {bedrooms} bedrooms, {furnishing}")
    else:
        price = format_price(property_details.get("price"))
        st.markdown(f"### {price} | {bedrooms} bedrooms")


def render_property_header(property_details: Dict[str, Any], property_id: str) -> None:
    """Render the property header with title, subtitle, and enquiry actions."""
    mode = determine_property_mode(property_details)

    address = property_details.get("address", "Unknown address")
    if isinstance(address, dict):
        address = address.get("displayAddress", "Unknown address")

    title = address

    st.title(title)

    col1, col2, col3 = st.columns([5, 1, 1])
    with col1:
        _render_subtitle(property_details, mode)

    with col2:
        if st.button(
            "✉️ Draft enquiry",
            key=f"draft_enquiry_{property_id}",
            type="primary"
        ):
            message = draft_enquiry(
                property_details=property_details,
                customer_name=st.session_state.get("first_name", "Customer"),
            )
            st.session_state[f"draft_msg_{property_id}"] = message
            st.session_state[f"show_draft_{property_id}"] = True

    with col3:
        st.link_button(
            "View original",
            url=f"https://www.rightmove.co.uk/properties/{property_id}"
        )
