from typing import Any, Dict, List, Optional

import streamlit as st

from app.modules.dashboard_utils import (
    get_journey_duration,
    get_preferred_location_label,
    get_sales_metrics,
    to_number,
)


def render_filter_controls(
    shortlist: List[Dict[str, Any]],
    mode: str,
    user_submission: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """Render filter widgets and return selected filter values."""
    filters: Dict[str, Any] = {}
    preferred_location = get_preferred_location_label(user_submission)
    content = user_submission.get("content", {}) if user_submission else {}

    with st.expander("Filters", expanded=False):
        filters["within_2km"] = st.checkbox(
            f"📍 Within 2km of {preferred_location}",
            help="Show only properties within 2km of your preferred location",
            key=f"{mode}_within_2km"
        )

        journey_default = content.get("max_commute_minutes")  # todo: not supported right now

        if mode == "sales":
            filters["chain_free"] = st.checkbox(
                "Chain free only",
                help="Only show properties identified as chain free",
                key="sales_chain_free"
            )

            lease_default = content.get("min_lease_year")  # todo: not supported right now
            filters["min_years_left_on_lease"] = st.number_input(
                "Minimum years left on lease",
                min_value=50,
                value=int(lease_default or 150),
                step=1,
                key="sales_min_years_left"
            )

            service_charge_default = content.get("max_service_charge")  # todo: not supported right now
            filters["max_service_charge"] = st.number_input(
                "Maximum annual service charge (£)",
                min_value=0,
                value=int(service_charge_default or 2000),
                step=100,
                key="sales_service_charge_limit"
            )

            filters["max_journey_minutes"] = st.number_input(  # todo: not supported right now
                "Maximum journey time (minutes)",
                min_value=5,
                value=int(journey_default or 60),
                step=5,
                key="sales_journey_limit"
            )
        else:
            furnish_types = sorted(
                {prop.get("furnish_type") for prop in shortlist if prop.get("furnish_type")}
            )
            filters["furnish_types"] = st.multiselect(
                "Furnishing type",
                options=furnish_types,
                default=[],
                key="rental_furnish_types"
            )

            deposit_default = content.get("max_deposit")
            filters["max_deposit"] = st.number_input(
                "Maximum deposit (£)",
                min_value=0,
                value=int(deposit_default or 2500),
                step=100,
                key="rental_deposit_limit"
            )

            filters["max_journey_minutes"] = st.number_input(
                "Maximum journey time (minutes)",
                min_value=5,
                value=int(journey_default or 60),
                step=5,
                key="rental_journey_limit"
            )

    return filters


def filter_properties(
    shortlist: List[Dict[str, Any]],
    mode: str,
    filters: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Apply selected filters to the shortlist."""
    filtered = shortlist

    if filters.get("within_2km"):
        filtered = [
            prop for prop in filtered
            if to_number(prop.get("distance_to_preferred_location")) is not None
            and to_number(prop.get("distance_to_preferred_location")) <= 2.0
        ]

    max_journey = filters.get("max_journey_minutes")
    if max_journey:
        filtered = [
            prop for prop in filtered
            if (journey := get_journey_duration(prop)) is None or journey <= max_journey
        ]

    if mode == "sales":
        if filters.get("chain_free"):
            filtered = [
                prop for prop in filtered
                if (prop.get("description_analysis", {}) or {}).get("is_chain_free") is True
            ]

        min_years = filters.get("min_years_left_on_lease")
        if min_years:
            filtered = [
                prop for prop in filtered
                if (metrics := get_sales_metrics(prop))["years_left_on_lease"] is None
                or metrics["years_left_on_lease"] >= min_years
            ]

        max_service_charge = filters.get("max_service_charge")
        if max_service_charge:
            filtered = [
                prop for prop in filtered
                if (metrics := get_sales_metrics(prop))["service_charge"] is None
                or metrics["service_charge"] <= max_service_charge
            ]
    else:
        furnish_types = filters.get("furnish_types")
        if furnish_types:
            filtered = [
                prop for prop in filtered
                if prop.get("furnish_type") in furnish_types
            ]

        max_deposit = filters.get("max_deposit")
        if max_deposit:
            filtered = [
                prop for prop in filtered
                if to_number(prop.get("deposit")) is not None
                and to_number(prop.get("deposit")) <= max_deposit
            ]

    return filtered
