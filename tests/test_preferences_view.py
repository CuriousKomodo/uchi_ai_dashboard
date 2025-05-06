import streamlit as st
from datetime import datetime, timezone

# Set page config
st.set_page_config(
    page_title="Preferences View Test",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Test data
test_submission = {
    'content': {
        'created_at': datetime(2025, 4, 14, 11, 48, 49, 765171, tzinfo=timezone.utc),
        'user_preference': "Bright natural light with plenty of storage. The kitchen and bathroom are installed with a modern standard. If all the rooms have wooden floor that'd be great. \n",
        'min_lease_year': 150,
        'num_bedrooms': 2,
        'first_name': 'Kefei',
        'workplace_location': 'EC2M7PY',
        'has_pet': 'Yes',
        'property_type': ['House', 'Apartment'],
        'email': 'hu.kefei@yahoo.co.uk',
        'max_price': 460,
        'has_child': 'No',
        'hobbies': 'I love going to the gym, and visiting local coffee shops and second hand shops. '
    },
    'user_id': 'hIk6crfW5BncLCYK8fIR',
    'email': 'hu.kefei@yahoo.co.uk',
    'id': 'F9snis9iLX2MqpHKq2ss'
}

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

with col1:
    # Budget and Property Type
    st.markdown('<div class="preference-section">', unsafe_allow_html=True)
    st.markdown('<div class="preference-label">💰 Budget</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="preference-value">£{test_submission["content"]["max_price"]:,}k</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preference-section">', unsafe_allow_html=True)
    st.markdown('<div class="preference-label">🏠 Property Type</div>', unsafe_allow_html=True)
    property_types = test_submission['content']['property_type']
    types_html = ''.join([f'<span class="preference-tag">{pt}</span>' for pt in property_types])
    st.markdown(f'<div>{types_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preference-section">', unsafe_allow_html=True)
    st.markdown('<div class="preference-label">🛏️ Bedrooms</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="preference-value">{test_submission["content"]["num_bedrooms"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preference-section">', unsafe_allow_html=True)
    st.markdown('<div class="preference-label">📅 Minimum Lease</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="preference-value">{test_submission["content"]["min_lease_year"]} years</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # Location and Lifestyle
    st.markdown('<div class="preference-section">', unsafe_allow_html=True)
    st.markdown('<div class="preference-label">📍 Workplace Location</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="preference-value">{test_submission["content"]["workplace_location"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preference-section">', unsafe_allow_html=True)
    st.markdown('<div class="preference-label">👨‍👩‍👧‍👦 Family Status</div>', unsafe_allow_html=True)
    family_status = []
    if test_submission['content']['has_child'] == 'Yes':
        family_status.append('Has Children')
    if test_submission['content']['has_pet'] == 'Yes':
        family_status.append('Has Pets')
    if not family_status:
        family_status = ['No Children', 'No Pets']
    status_html = ''.join([f'<span class="preference-tag">{status}</span>' for status in family_status])
    st.markdown(f'<div>{status_html}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preference-section">', unsafe_allow_html=True)
    st.markdown('<div class="preference-label">🎯 Hobbies & Interests</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="preference-value">{test_submission["content"]["hobbies"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="preference-section">', unsafe_allow_html=True)
    st.markdown('<div class="preference-label">💭 Additional Preferences</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="preference-value">{test_submission["content"]["user_preference"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Add a note about this being a test
st.info("This is a test view of the preferences section. The actual implementation will be integrated into the main dashboard.") 