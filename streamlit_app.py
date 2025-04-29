import streamlit as st
from connection.firestore import FireStore
from app.modules.dashboard import show_dashboard, login
from app.modules.chat import show_chat_interface

# Initialize Firestore
firestore = FireStore(credential_info=st.secrets["firestore_credentials"])

# Set page config
st.set_page_config(
    page_title="Uchi AI Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "last_access_time" not in st.session_state:
    st.session_state.last_access_time = {}
if "user_sort_order" not in st.session_state:
    st.session_state.user_sort_order = ""
if "chat_flag" not in st.session_state:
    st.session_state.chat_flag = None

def main():
    """Main app function."""
    # Check if we're in chat mode
    if any(key in st.query_params for key in ["property_id", "address", "price", "bedrooms"]):
        show_chat_interface()
    else:
        show_dashboard(firestore)

if __name__ == "__main__":
    main() 