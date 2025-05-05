import streamlit as st
from connection.firestore import FireStore
from app.modules.dashboard import show_dashboard, login
from app.modules.chat import show_chat_interface
from app.modules.school_view import school_map_view_with_properties
from app.modules.property_page import show_property_page

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
if "current_view" not in st.session_state:
    st.session_state.current_view = "dashboard"

def main():
    """Main app function."""
    # Check if we're in property page mode
    if "property_id" in st.query_params:
        show_property_page(firestore)
    else:
        # Get the current path and query parameters
        path = st.query_params.get("path", "dashboard")
        
        # Handle chat view
        if any(key in st.query_params for key in ["property_id", "address", "price", "bedrooms"]):
            show_chat_interface()
            return
        
        # Handle school view
        if path == "school":
            st.session_state.current_view = "school"
        else:
            st.session_state.current_view = "dashboard"

        # Show view selector at the top only if user is authenticated
        if st.session_state.authenticated:
            st.markdown("### Select View")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🏠 Dashboard View", use_container_width=True, 
                            type="primary" if st.session_state.current_view == "dashboard" else "secondary"):
                    st.query_params.update(path="dashboard")
                    st.rerun()
            with col2:
                if st.button("🏫 School-centric View", use_container_width=True,
                            type="primary" if st.session_state.current_view == "school" else "secondary"):
                    st.query_params.update(path="school")
                    st.rerun()
            st.markdown("---")  # Add a separator line

        # Show the appropriate view
        if st.session_state.current_view == "school":
            # Get user's shortlist for the school view
            if st.session_state.authenticated:
                shortlist = firestore.get_shortlists_by_user_id(st.session_state.user_id)
                school_map_view_with_properties({}, shortlist)
            else:
                login(firestore)
        else:
            show_dashboard(firestore)

if __name__ == "__main__":
    import sys
    import os
    
    # Check if we're in debug mode
    if "--debug" in sys.argv:
        # Enable debugger
        import debugpy
        debugpy.listen(5678)
        print("Waiting for debugger to attach...")
        debugpy.wait_for_client()
        print("Debugger attached!")
        
        # Set Streamlit debug flags
        os.environ["STREAMLIT_SERVER_PORT"] = "8501"
        os.environ["STREAMLIT_SERVER_ADDRESS"] = "localhost"
        os.environ["STREAMLIT_SERVER_HEADLESS"] = "false"
        os.environ["STREAMLIT_SERVER_ENABLE_CORS"] = "true"
    
    # Run the app
    main() 