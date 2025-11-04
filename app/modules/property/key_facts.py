import re
from typing import Any, Dict, List, Tuple

import streamlit as st

from app.modules.property.utils import (
    determine_property_mode,
    format_currency,
    format_let_available,
    value_or_placeholder,
)


def _get_description_value(property_details: Dict[str, Any], key: str) -> Any:
    """Fetch value from description analysis or top-level fallback."""
    description = property_details.get("description_analysis") or {}
    value = description.get(key)
    if value in (None, "", "None"):
        value = property_details.get(key)
    return value


def _sales_key_facts(property_details: Dict[str, Any]) -> List[Tuple[str, str]]:
    years_left = _get_description_value(property_details, "years_left_on_lease")
    chain_free = _get_description_value(property_details, "is_chain_free")
    service_charge = _get_description_value(property_details, "service_charge")

    years_display = value_or_placeholder(years_left)
    try:
        years_numeric = float(years_left)
        years_display = f"{int(years_numeric)} years"
    except (TypeError, ValueError):
        pass

    facts = [
        ("Years left on lease", years_display),
        ("Chain free", value_or_placeholder(chain_free)),
        ("Service charge", format_currency(service_charge)),
    ]
    return facts


def _resolve_rental_availability(property_details: Dict[str, Any]) -> str:
    """Pick a rental availability value formatted as YYYY-mm-dd."""
    description = property_details.get("description_analysis") or {}
    candidates = [
        description.get("let_available"),
        property_details.get("let_available"),
    ]

    for value in candidates:
        if isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return format_let_available(value)
    return "Ask agent"


def _rental_key_facts(property_details: Dict[str, Any]) -> List[Tuple[str, str]]:
    deposit = property_details.get("deposit") or _get_description_value(property_details, "deposit")
    tenancy = property_details.get("minimum_tenancy_months") or _get_description_value(property_details, "minimum_tenancy_months")

    tenancy_display = value_or_placeholder(tenancy)
    try:
        tenancy_numeric = float(tenancy)
        tenancy_display = f"{int(tenancy_numeric)} months"
    except (TypeError, ValueError):
        pass

    facts = [
        ("Available from", _resolve_rental_availability(property_details)),
        ("Deposit", format_currency(deposit)),
        ("Minimum tenancy", tenancy_display),
    ]
    return facts


def render_key_facts(property_details: Dict[str, Any]) -> None:
    """Render the key facts section."""
    mode = determine_property_mode(property_details)
    facts = _sales_key_facts(property_details) if mode == "sales" else _rental_key_facts(property_details)

    st.markdown("#### Key Facts")
    with st.container(border=True):
        for label, value in facts:
            st.markdown(f"**{label}:** {value}")
