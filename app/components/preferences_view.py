import streamlit as st
from typing import Dict, Any

def show_preferences_section(submission_data: Dict[str, Any]) -> None:
    """Display a user's property preferences in a nicely formatted section.
    
    Args:
        submission_data (Dict[str, Any]): The submission data containing user preferences
    """
    # Create a container for preferences with a nice background
    st.markdown("""
        <style>
        .preference-title {
            color: #2c3e50;
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .preference-label {
            color: #6c757d;
            font-size: 0.9em;
            margin-bottom: 5px;
        }
        .preference-value {
            color: #2c3e50;
            font-size: 1.1em;
            font-weight: 500;
            margin-bottom: 8px;
        }
        .preference-tag {
            display: inline-block;
            background-color: #e3f2fd;
            color: #1976d2;
            padding: 4px 12px;
            border-radius: 15px;
            margin: 2px;
            font-size: 0.9em;
        }
        .key-preference-label {
            color: #2c3e50;
            font-size: 1.1em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .key-preference-value {
            color: #1976d2;
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 8px;
        }
        .section-title {
            color: #2c3e50;
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        }
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
            padding: 12px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="preference-title">✨ Your Property Preferences</div>', unsafe_allow_html=True)
    
    content = submission_data.get('content', {})
    
    # Top row with key preferences
    key_col1, key_col2, key_col3 = st.columns(3)
    
    with key_col1:
        with st.container(border=True):
            st.markdown('<div class="key-preference-label">💰 Budget</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="key-preference-value">£{content.get("max_price", 0):,}k</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    with key_col2:
        with st.container(border=True):
            st.markdown('<div class="key-preference-label">🏠 Property Type</div>', unsafe_allow_html=True)
            property_types = content.get('property_type', [])
            types_html = ''.join([f'<span class="preference-tag">{pt}</span>' for pt in property_types])
            st.markdown(f'<div>{types_html}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    with key_col3:
        with st.container(border=True):
            st.markdown('<div class="key-preference-label">🛏️ Bedrooms</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="key-preference-value">{content.get("num_bedrooms", 0)}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main sections: Property Requirements and Lifestyle
    req_col, lifestyle_col = st.columns(2)
    
    with req_col:
        with st.container(border=True):
            st.markdown('<div class="section-title">🏡 Property Requirements</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="preference-label">📅 Minimum Lease</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="preference-value">{content.get("min_lease_year", 0)} years</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="preference-label">🎯 First Time Buyer</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="preference-value">{content.get("is_first_time_buyer", "Not specified")}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="preference-label">💭 Additional Details</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="preference-value">{content.get("user_preference", "Not specified")}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

    with lifestyle_col:
        with st.container(border=True):
            st.markdown('<div class="section-title">👨‍👩‍👧‍👦 Lifestyle & Neighborhood </div>', unsafe_allow_html=True)
            
            st.markdown('<div class="preference-label">📍 Workplace Location</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="preference-value">{content.get("workplace_location", "Not specified")}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="preference-label">👨‍👩‍👧‍👦 Family Status</div>', unsafe_allow_html=True)
            family_status = []
            if content.get('has_child') == 'Yes':
                family_status.append('Has Children')
            if content.get('has_pet') == 'Yes':
                family_status.append('Has Pets')
            if not family_status:
                family_status = ['No Children', 'No Pets']
            status_html = ''.join([f'<span class="preference-tag">{status}</span>' for status in family_status])
            st.markdown(f'<div>{status_html}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="preference-label">🎯 Hobbies & Interests</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="preference-value">{content.get("hobbies", "Not specified")}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)