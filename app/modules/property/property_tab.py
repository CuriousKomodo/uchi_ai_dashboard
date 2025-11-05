import base64
from typing import Any, Dict, List

import streamlit as st

from app.components.criteria_components import render_property_criteria
from app.modules.property.comparison_chart import render_price_comparison_chart
from app.modules.property.key_facts import render_key_facts
from app.modules.property.utils import determine_property_mode, value_or_placeholder
from utils.demographic_utils import (
    format_description_analysis_value,
    snake_case_to_title,
)
from utils.text_utils import extract_conclusion


def render_ai_summary(property_details: Dict[str, Any]) -> None:
    """Display AI-generated notes and compatibility score."""
    images_conclusion = extract_conclusion(property_details.get("image_analysis", ""))
    if images_conclusion:
        st.markdown("### UchiAI's notes")
        st.markdown(images_conclusion)

    # compatibility_score = property_details.get("prop_criteria_matched")
    # if isinstance(compatibility_score, (int, float)):
    #     st.markdown(f"#### Compatibility score: {round(float(compatibility_score), 2) * 100:.0f}%")


def _get_additional_description_items(mode: str, property_details: Dict[str, Any]) -> Dict[str, Any]:
    """Return description analysis items excluding those prioritised elsewhere."""
    exclude_keys = {"features"}
    if mode == "sales":
        exclude_keys.update({"years_left_on_lease", "is_chain_free", "service_charge"})
    else:
        exclude_keys.update({"let_available", "available_from", "deposit", "minimum_tenancy_months"})

    description = property_details.get("description_analysis") or {}
    return {k: v for k, v in description.items() if k not in exclude_keys}


def render_additional_information(mode: str, property_details: Dict[str, Any]) -> None:
    """Render supplementary property information."""
    st.markdown("#### Property Details")
    with st.container(border=True):
        additional_items = _get_additional_description_items(mode, property_details)
        if not additional_items:
            st.markdown("*No AI extracted information available*")
            return

        for key, value in additional_items.items():
            formatted_key = snake_case_to_title(key)
            formatted_value = format_description_analysis_value(value)
            st.markdown(f"**{formatted_key}:** {formatted_value}")


def render_features_section(property_details: Dict[str, Any]) -> None:
    """Display property features in a grid layout."""
    features_to_display: List[str] = []
    description_features = property_details.get("description_analysis", {}).get("features") or []
    features_to_display.extend(description_features)

    property_features = property_details.get("features") or []
    for feature in property_features:
        if feature not in features_to_display:
            features_to_display.append(feature)

    if not features_to_display:
        return

    st.markdown("#### Key Features")
    st.markdown(
        """
        <style>
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            margin: 15px 0;
        }
        .feature-item {
            background-color: #f0f2f6;
            padding: 10px 15px;
            border-radius: 5px;
            font-size: 16px;
            display: flex;
            align-items: center;
        }
        .feature-item::before {
            content: "✓";
            color: #00acb5;
            font-weight: bold;
            margin-right: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    features_html = '<div class="feature-grid">'
    for feature in features_to_display:
        features_html += f'<div class="feature-item">{feature}</div>'
    features_html += "</div>"
    st.markdown(features_html, unsafe_allow_html=True)


def render_floorplan_and_epc(property_details: Dict[str, Any]) -> None:
    """Render floorplan and EPC sections side by side."""
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Floorplan")
        with st.container(border=True):
            floorplan_data = property_details.get("floorplan")
            if isinstance(floorplan_data, list) and floorplan_data:
                floorplan_data = floorplan_data[0]

            if isinstance(floorplan_data, str):
                try:
                    decoded_floorplan = base64.b64decode(floorplan_data)
                    st.image(decoded_floorplan, caption="Floorplan", width=260)
                except Exception:
                    st.markdown("Ask agent for floorplan")
            elif isinstance(floorplan_data, dict) and floorplan_data.get("url"):
                st.image(floorplan_data["url"], caption="Floorplan", width=260)
            elif floorplan_data:
                st.markdown("Ask agent for floorplan")
            else:
                st.info("Ask agent for floorplan")

    with col2:
        st.markdown("#### Energy Performance Certificate")
        with st.container(border=True):
            epc = property_details.get("epc")
            if epc:
                try:
                    if isinstance(epc, str) and epc.startswith("data:image"):
                        st.image(epc, caption="EPC Rating", width=260)
                    elif isinstance(epc, str):
                        st.image(epc, caption="EPC Rating", width=260)
                    else:
                        st.error("Invalid EPC image format")
                except Exception as exc:
                    st.error(f"Error displaying EPC: {exc}")
            else:
                st.info("EPC not available")


def render_property_tab(property_details: Dict[str, Any]) -> None:
    """Render the full property tab with AI summary, key facts, and supporting info."""
    mode = determine_property_mode(property_details)

    summary_col, _, chart_col = st.columns([5, 1, 3])
    with summary_col:
        render_ai_summary(property_details)
    with chart_col:
        st.markdown("#### Price comparison")
        render_price_comparison_chart(property_details)

    with st.container():
        render_property_criteria(property_details)

    render_key_facts(property_details)
    render_additional_information(mode, property_details)

    render_features_section(property_details)
    render_floorplan_and_epc(property_details)
