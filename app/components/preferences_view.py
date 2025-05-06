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
        .preference-container {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
        }
        .preference-title {
            color: #2c3e50;
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .preference-section {
            margin: 10px 0;
            padding: 10px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
        </style>
    """, unsafe_allow_html=True)

    # Main preferences container
    st.markdown('<div class="preference-container">', unsafe_allow_html=True)
    st.markdown('<div class="preference-title">✨ Your Property Preferences</div>', unsafe_allow_html=True)
    
    # Create two columns for layout
    col1, col2 = st.columns(2)
    
    content = submission_data.get('content', {})
    
    with col1:
        # Budget and Property Type
        st.markdown('<div class="preference-section">', unsafe_allow_html=True)
        st.markdown('<div class="preference-label">💰 Budget</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="preference-value">£{content.get("max_price", 0):,}k</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="preference-section">', unsafe_allow_html=True)
        st.markdown('<div class="preference-label">🏠 Property Type</div>', unsafe_allow_html=True)
        property_types = content.get('property_type', [])
        types_html = ''.join([f'<span class="preference-tag">{pt}</span>' for pt in property_types])
        st.markdown(f'<div>{types_html}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="preference-section">', unsafe_allow_html=True)
        st.markdown('<div class="preference-label">🛏️ Bedrooms</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="preference-value">{content.get("num_bedrooms", 0)}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="preference-section">', unsafe_allow_html=True)
        st.markdown('<div class="preference-label">📅 Minimum Lease</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="preference-value">{content.get("min_lease_year", 0)} years</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Location and Lifestyle
        st.markdown('<div class="preference-section">', unsafe_allow_html=True)
        st.markdown('<div class="preference-label">📍 Workplace Location</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="preference-value">{content.get("workplace_location", "Not specified")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="preference-section">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="preference-section">', unsafe_allow_html=True)
        st.markdown('<div class="preference-label">🎯 Hobbies & Interests</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="preference-value">{content.get("hobbies", "Not specified")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="preference-section">', unsafe_allow_html=True)
        st.markdown('<div class="preference-label">💭 Additional Preferences</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="preference-value">{content.get("user_preference", "Not specified")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True) 