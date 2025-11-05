from datetime import datetime
from typing import Any, Dict, Optional


def determine_property_mode(property_details: Dict[str, Any]) -> str:
    """Determine whether a property should be treated as sales or rental."""
    if property_details.get("monthly_rent") is not None:
        return "rental"
    return "sales"


def format_currency(value: Optional[Any]) -> str:
    """Format numeric values as currency with thousands separators."""
    if value in (None, "", "None"):
        return "N/A"
    try:
        return f"£{int(float(value)):,}"
    except (TypeError, ValueError):
        return "N/A"


def format_price(value: Optional[Any]) -> str:
    """Format property sale price."""
    return format_currency(value)


def format_rent(value: Optional[Any]) -> str:
    """Format monthly rent."""
    formatted = format_currency(value)
    return f"{formatted} pcm" if formatted.startswith("£") else formatted


def value_or_placeholder(value: Any, placeholder: str = "Ask agent") -> str:
    """Return value converted to string, falling back to placeholder when missing."""
    if value in (None, "", [], {}, "None"):
        return placeholder
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, (list, tuple, set)):
        return ", ".join(str(item) for item in value) if value else placeholder
    return str(value)


def get_neighborhood_metric(property_details: Dict[str, Any], key: str) -> Optional[Any]:
    """Extract a metric from neighborhood info if available."""
    neighborhood_info = property_details.get("neighborhood_info") or {}
    return neighborhood_info.get(key)


def format_let_available(availability: Any) -> str:
    """Convert availability value to a readable date string."""
    if availability in (None, "", "None", 0):
        return "Ask agent"

    def _format(dt: datetime) -> str:
        return dt.strftime("%d %b %Y")

    if isinstance(availability, (int, float)):
        timestamp = float(availability)
        if timestamp > 1e12:
            timestamp /= 1000.0
        try:
            return _format(datetime.fromtimestamp(timestamp))
        except (OSError, OverflowError):
            return "Ask agent"

    if isinstance(availability, str):
        try:
            normalized = availability.replace("Z", "+00:00")
            dt_obj = datetime.fromisoformat(normalized)
            return _format(dt_obj)
        except ValueError:
            return availability

    return str(availability)
