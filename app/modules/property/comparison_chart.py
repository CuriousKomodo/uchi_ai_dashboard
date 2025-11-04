from typing import Any, Dict, Optional

import altair as alt
import pandas as pd
import streamlit as st

from app.modules.property.utils import (
    determine_property_mode,
    format_currency,
    get_neighborhood_metric,
)


def _to_number(value: Any) -> Optional[float]:
    """Convert potential numeric representations into float."""
    if value in (None, "", "Ask agent", "None"):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = "".join(ch for ch in value if ch.isdigit() or ch in {".", ","})
        cleaned = cleaned.replace(",", "")
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _get_average_value(property_details: Dict[str, Any], mode: str) -> Optional[Any]:
    """Return the neighborhood average value relevant to the mode."""
    candidates = []
    if mode == "sales":
        candidates = ["asking_price", "average_price", "avg_price"]
    else:
        candidates = ["asking_rent", "average_rent", "avg_rent"]

    for key in candidates:
        value = get_neighborhood_metric(property_details, key)
        if value not in (None, "", "None"):
            return value
    return None


def render_price_comparison_chart(property_details: Dict[str, Any]) -> None:
    """Render a comparison bar chart between property value and neighborhood average."""
    mode = determine_property_mode(property_details)
    property_value = property_details.get("price") if mode == "sales" else property_details.get("monthly_rent")
    average_value = _get_average_value(property_details, mode)

    property_number = _to_number(property_value)
    average_number = _to_number(average_value)

    if property_number is None and average_number is None:
        st.info("Data not available")
        return

    data = []
    if property_number is not None:
        data.append({
            "Category": "This property",
            "Value": property_number,
        })

    if average_number is not None:
        label = "Avg. sale price" if mode == "sales" else "Avg. rent"
        data.append({
            "Category": label,
            "Value": average_number,
        })

    if not data:
        st.info("Data not available")
        return

    st.caption(f"This property vs. other {property_details.get('num_bedrooms')}-bedroom properties in the area")
    df = pd.DataFrame(data)
    chart = alt.Chart(df).mark_bar(size=45, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
        y=alt.Y("Category:N", title=""),
        x=alt.X("Value:Q", title="Price (£)" if mode == "sales" else "Rent (£ pcm)"),
        color=alt.Color("Category:N", legend=None, scale=alt.Scale(range=["#00acb5", "#6c757d"])),
        tooltip=[
            alt.Tooltip("Category:N", title=""),
            alt.Tooltip("Value:Q", title="Amount", format=",")
        ]
    ).properties(
        height=200
    )

    st.altair_chart(chart, use_container_width=True)
