from typing import Any, Dict, List

import streamlit as st

from app.modules.dashboard_utils import clear_all_caches, determine_listing_mode


SALES_SORT_OPTIONS = [
    "Criteria Match: Most to Least",
    "Price: Low to High",
    "Price: High to Low",
    "Bedrooms: Most to Fewest",
    "Closest to the preferred location",
    "Newest First",
]

RENTAL_SORT_OPTIONS = [
    "Criteria Match: Most to Least",
    "Rent: Low to High",
    "Rent: High to Low",
    "Bedrooms: Most to Fewest",
    "Closest to the preferred location",
    "Newest First",
]


def render_listing_mode_selector(shortlist: List[Dict[str, Any]]) -> str:
    """Offer a toggle between sales and rental listings."""
    default_mode = determine_listing_mode(shortlist)
    has_rental = any(prop.get("monthly_rent") is not None for prop in shortlist)

    options = ["Sales", "Rental"] if has_rental else ["Sales"]
    default_index = 1 if default_mode == "rental" and has_rental else 0

    selected = st.radio(
        "Listing type",
        options=options,
        index=default_index,
        horizontal=True,
        key="listing_type_selector"
    )
    return selected.lower()


def render_sort_control(mode: str) -> str:
    """Render the sort dropdown for the selected mode."""
    options = SALES_SORT_OPTIONS if mode == "sales" else RENTAL_SORT_OPTIONS
    default_option = "Criteria Match: Most to Least"

    sort_choice = st.selectbox(
        "Sort by",
        options=options,
        index=options.index(default_option),
        placeholder=default_option,
        key=f"{mode}_sort_choice"
    )
    return sort_choice


def render_refresh_button() -> None:
    """Provide a refresh button that clears cached data."""
    if st.button("🔄 Refresh Properties", type="secondary"):
        clear_all_caches()
        st.rerun()
