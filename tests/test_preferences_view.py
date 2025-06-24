import streamlit as st
from datetime import datetime, timezone

from preferences_view import show_preferences_section


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

# Display the preferences section
show_preferences_section(test_submission)

# Add a note about this being a test
st.info("This is a test view of the preferences section. The actual implementation will be integrated into the main dashboard.") 