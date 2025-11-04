import base64
from collections.abc import Iterable
from typing import Any, Dict

import streamlit as st

from app.modules.dashboard_utils import (
    format_currency,
    format_let_available,
    get_journey_duration,
    to_number,
)


def _value_indicates_match(value: Any) -> bool:
    """Interpret various value types that indicate a successful match."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value > 0
    if isinstance(value, str):
        normalized = value.strip().lower()
        return normalized in {"true", "yes", "matched", "match", "1"}
    if isinstance(value, dict):
        return any(_value_indicates_match(inner) for inner in value.values())
    return False


def _collect_criteria_tags(prop: Dict[str, Any]) -> Dict[str, bool]:
    """Aggregate match indicators from different property fields."""
    tags: Dict[str, bool] = {}

    for source_key in ("match_output", "matched_criteria", "matched_lifestyle_criteria"):
        source = prop.get(source_key)
        if isinstance(source, dict):
            for key, value in source.items():
                if _value_indicates_match(value) or value is None:
                    tags[key] = True
        elif isinstance(source, Iterable) and not isinstance(source, (str, bytes)):
            for item in source:
                if isinstance(item, str):
                    tags[item] = True
                elif isinstance(item, dict):
                    for key, value in item.items():
                        if _value_indicates_match(value) or value is None:
                            tags[key] = True

    return tags


def render_property_card(prop: Dict[str, Any], mode: str) -> None:
    """Render a single property card."""
    with st.container(border=True):
        if prop.get("compressed_images"):
            try:
                if prop["property_id"] not in st.session_state.decoded_images:
                    raw_image = prop["compressed_images"][0]
                    if isinstance(raw_image, str):
                        decoded_image = base64.b64decode(raw_image)
                    elif isinstance(raw_image, dict):
                        decoded_image = base64.b64decode(raw_image.get("base64", ""))
                    else:
                        decoded_image = None

                    if decoded_image:
                        st.session_state.decoded_images[prop["property_id"]] = [decoded_image]

                if prop["property_id"] in st.session_state.decoded_images:
                    st.image(
                        st.session_state.decoded_images[prop["property_id"]][0],
                        use_column_width=True
                    )
            except Exception as exc:
                print(f"Error displaying image for property {prop['property_id']}: {exc}")
                st.write("No image available")

        address = prop.get("address", "Unknown address")
        if isinstance(address, dict):
            address = address.get("displayAddress", "Unknown address")
        st.markdown(f'<div class="property-title">{address}</div>', unsafe_allow_html=True)

        if mode == "sales":
            price_value = to_number(prop.get("price"))
            price_text = format_currency(price_value)
            if price_text:
                st.markdown(f'<div class="property-price">£{price_text}</div>', unsafe_allow_html=True)
        else:
            rent_value = to_number(prop.get("monthly_rent"))
            rent_text = format_currency(rent_value)
            if rent_text:
                st.markdown(f'<div class="property-price">£{rent_text} pcm</div>', unsafe_allow_html=True)

        bedrooms = prop.get("num_bedrooms", 0) or 0
        bathrooms = prop.get("num_bathrooms", 0) or 0
        details_text = f"🛏️ {bedrooms} bed{'s' if bedrooms != 1 else ''}"
        if bathrooms:
            details_text += f" | 🚿 {bathrooms} bathroom{'s' if bathrooms != 1 else ''}"
        st.markdown(f'<div class="property-details">{details_text}</div>', unsafe_allow_html=True)

        commute_minutes = get_journey_duration(prop)
        if mode == "sales" and commute_minutes is not None:
            st.markdown(
                f'<div class="property-details">🚆 Commute: {int(commute_minutes)} min</div>',
                unsafe_allow_html=True
            )

        if mode == "rental":
            furnish_type = prop.get("furnish_type")
            availability_label = format_let_available(prop.get("let_available"))
            tenancy_months = prop.get("minimum_tenancy_months")

            if furnish_type:
                st.markdown(
                    f'<div class="property-details">🛋️ Furnishing: {furnish_type}</div>',
                    unsafe_allow_html=True
                )
            if commute_minutes is not None:
                st.markdown(
                    f'<div class="property-details">🚆 Commute: {int(commute_minutes)} min</div>',
                    unsafe_allow_html=True
                )
            if availability_label:
                st.markdown(
                    f'<div class="property-details">📅 Available from {availability_label}</div>',
                    unsafe_allow_html=True
                )
            if tenancy_months:
                st.markdown(
                    f'<div class="property-details">📄 Minimum tenancy: {tenancy_months} months</div>',
                    unsafe_allow_html=True
                )

        match_criteria = _collect_criteria_tags(prop)

        distance_to_preferred_locations = prop.get("distance_to_preferred_locations", {})
        if distance_to_preferred_locations:
            for location, distance in distance_to_preferred_locations.items():
                distance_value = to_number(distance)
                if distance_value is not None and distance_value < 2.5:
                    st.markdown(f"~{int(distance_value)} miles to {location}", unsafe_allow_html=True)

        criteria_html = '<div style="margin: 10px 0;">'
        for key, value in match_criteria.items():
            if isinstance(value, bool) and value:
                criteria_html += f'<span class="criteria-tag">{key.replace("_", " ").capitalize()}</span>'
        criteria_html += "</div>"
        st.markdown(criteria_html, unsafe_allow_html=True)

        if st.button(
            "View Details",
            key=f"detail_{prop['property_id']}",
            use_container_width=True,
            type="primary"
        ):
            st.query_params.update(property_id=prop["property_id"])
            st.rerun()
