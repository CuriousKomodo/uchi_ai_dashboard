from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st


def clear_all_caches() -> None:
    """Clear cached data from session state."""
    for key in ("property_shortlist", "decoded_images", "user_submission"):
        if hasattr(st.session_state, key):
            delattr(st.session_state, key)


def determine_listing_mode(shortlist: List[Dict[str, Any]]) -> str:
    """Infer predominant listing type from available properties."""
    if not shortlist:
        return "sales"

    rental_count = sum(1 for prop in shortlist if prop.get("monthly_rent") is not None)
    sales_count = sum(1 for prop in shortlist if prop.get("price") is not None)
    return "rental" if rental_count and rental_count >= sales_count else "sales"


def filter_shortlist_by_mode(
    shortlist: List[Dict[str, Any]],
    mode: str
) -> List[Dict[str, Any]]:
    """Filter shortlist to sales or rental properties."""
    if mode == "rental":
        return [prop for prop in shortlist if prop.get("monthly_rent") is not None]
    return [prop for prop in shortlist if prop.get("price") is not None]


def get_preferred_location_label(user_submission: Optional[Dict[str, Any]]) -> str:
    """Extract the preferred location label for the user."""
    preferred_location = "your preferred location"
    if user_submission and user_submission.get("content"):
        preferred_raw = user_submission["content"].get("preferred_location")
        if preferred_raw:
            preferred_location = preferred_raw.split(",")[0]
    return preferred_location


def to_number(value: Any) -> Optional[float]:
    """Convert a value to float where possible."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = "".join(ch for ch in value if ch.isdigit() or ch in {".", ","})
        cleaned = cleaned.replace(",", "")
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def format_currency(value: Optional[float]) -> Optional[str]:
    """Format numeric value as currency string."""
    if value is None:
        return None
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return None


def format_let_available(availability: Any) -> Optional[str]:
    """Convert availability timestamp/ISO string into human-readable date."""
    if availability in (None, "", 0):
        return None

    def _format(dt: datetime) -> str:
        return dt.strftime("%d %b %Y")

    if isinstance(availability, (int, float)):
        timestamp = float(availability)
        if timestamp > 1e12:
            timestamp /= 1000.0
        try:
            return _format(datetime.fromtimestamp(timestamp))
        except (OSError, OverflowError):
            return None

    if isinstance(availability, str):
        try:
            normalized = availability.replace("Z", "+00:00")
            dt_obj = datetime.fromisoformat(normalized)
            return _format(dt_obj)
        except ValueError:
            return None

    return None


def get_sales_metrics(prop: Dict[str, Any]) -> Dict[str, Optional[float]]:
    """Extract numeric metrics used in sales filters."""
    description = prop.get("description_analysis", {}) or {}
    years_left = description.get("years_left_on_lease")
    service_charge = description.get("service_charge")

    if years_left is None:
        years_left = prop.get("length_of_lease")
    if service_charge is None:
        service_charge = prop.get("service_charge")

    return {
        "years_left_on_lease": to_number(years_left),
        "service_charge": to_number(service_charge),
    }


def get_journey_duration(prop: Dict[str, Any]) -> Optional[float]:
    """Return journey duration in minutes if available."""
    journey = prop.get("journey") or {}
    for key in ("total", "duration"):
        value = journey.get(key)
        duration = to_number(value)
        if duration is not None:
            return duration
    return None
