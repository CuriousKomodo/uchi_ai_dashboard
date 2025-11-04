import streamlit as st

from utils.image_utils import render_property_images

from connection.firestore import FireStore
from app.components.location_components import render_location_tab
from app.modules.property.header import render_property_header
from app.modules.property.property_tab import render_property_tab




def render_draft_expander(property_id):
    """Render the draft enquiry expander if it should be shown."""
    if st.session_state.get(f"show_draft_{property_id}", False):
        with st.expander("✉️ Edit your enquiry", expanded=True):
            # Get the draft message
            draft_message = st.session_state.get(f"draft_msg_{property_id}", "")
            
            # Text area for editing
            edited_message = st.text_area(
                "Your enquiry message:",
                value=draft_message,
                height=200,
                key=f"textarea_{property_id}"
            )
            
            # Action buttons
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.link_button(
                    "📧 Send enquiry", 
                    url=f"https://www.rightmove.co.uk/property-for-sale/contactBranch.html?propertyId={property_id}",
                    use_container_width=True
                )
            
            with col2:
                if st.button("❌ Close", key=f"close_draft_{property_id}", use_container_width=True):
                    st.session_state[f"show_draft_{property_id}"] = False
                    st.rerun()
            
            st.info("💡 To copy the text above, select all (Ctrl+A / Cmd+A) and copy (Ctrl+C / Cmd+C)")

def show_property_page(firestore: FireStore):
    """Show the property detail page."""
    # Get property ID from query parameters
    property_id = st.query_params.get("property_id", "")
    if not property_id:
        st.error("No property ID provided")
        return

    # Try to get property details from session state first
    property_details = None
    if hasattr(st.session_state, 'property_shortlist'):
        shortlist = st.session_state.property_shortlist
        property_details = shortlist.get(property_id)
        if property_details is None:
            try:
                property_details = shortlist.get(int(property_id))
            except (TypeError, ValueError):
                property_details = None
    
    # If not in session state, fetch from Firestore
    if not property_details:
        print(f"Property {property_id} not found in session state, fetching from Firestore")
        property_details = firestore.get_property_by_id(property_id)
        if not property_details:
            st.error("Property not found")
            return
        print(f"Fetched from Firestore, available fields: {list(property_details.keys())}")

    # Back to dashboard button
    if st.button("← Back to Dashboard", key="back_to_dashboard_from_property"):
        st.query_params.clear()
        st.rerun()

    # Property header with draft enquiry button
    render_property_header(property_details, property_id)
    
    # Draft enquiry expander (appears right after header)
    render_draft_expander(property_id)

    # Display images in a 2x4 grid
    render_property_images(property_details, property_id)

    # Property details in tabs
    tab1, tab2 = st.tabs(["Property Details", "Location"])

    with tab1:
        render_property_tab(property_details)

    with tab2:
        user_submission = st.session_state.get("user_submission")
        render_location_tab(property_details, user_submission)

    # with tab3:
    #     show_chat_interface()
