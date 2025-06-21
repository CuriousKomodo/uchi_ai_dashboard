import base64
import streamlit as st

from utils.draft import draft_enquiry

from connection.firestore import FireStore
from app.modules.chat import show_chat_interface
from app.components.criteria_components import render_property_criteria, render_lifestyle_criteria

from utils.text_utils import extract_conclusion
from utils.demographic_utils import (
    snake_case_to_title, 
    format_description_analysis_value,
)
from app.components.location_components import render_location_tab

def render_property_images(property_details, property_id):
    """Render property images in a 2x4 grid."""
    if property_details.get('compressed_images'):
        # Create 2 rows of 4 columns
        for row in range(2):
            cols = st.columns(4)
            for col in range(4):
                idx = row * 4 + col
                if idx < len(property_details['compressed_images']):
                    try:
                        # Decode image if not already in session state
                        if f"img_{property_id}_{idx}" not in st.session_state:
                            decoded_image = base64.b64decode(property_details['compressed_images'][idx]["base64"])
                            st.session_state[f"img_{property_id}_{idx}"] = decoded_image
                        
                        with cols[col]:
                            st.image(
                                st.session_state[f"img_{property_id}_{idx}"],
                                use_column_width=True
                            )
                    except Exception as e:
                        print(f"Error displaying image {idx} for property {property_id}: {str(e)}")

def render_ai_notes(property_details):
    """Render AI notes from image analysis."""
    images_conclusion = extract_conclusion(property_details.get("image_analysis", ""))
    if images_conclusion:
        st.markdown("### UchiAI's notes")
        st.markdown(images_conclusion)
    compatibility_score = property_details.get("prop_property_criteria_matched")
    if compatibility_score and isinstance(compatibility_score, float):
        st.markdown(f"#### Compatibility score: {round(compatibility_score, 2)*100} %")

def render_property_details_tab(property_details):
    """Render the Property Details tab content."""
    # Render matched criteria using the new components
    render_property_criteria(property_details)
    # render_lifestyle_criteria(property_details)

    # Display property details
    st.markdown("#### Property Details")
    with st.container(border=True):
        st.markdown("**Additional Information**")
        description_analysis = property_details.get('description_analysis', {})

        if description_analysis:
            # Skip 'features' as it's displayed separately below
            for key, value in description_analysis.items():
                if key != 'features':
                    formatted_key = snake_case_to_title(key)
                    formatted_value = format_description_analysis_value(value)
                    st.markdown(f"**{formatted_key}:** {formatted_value}")
        else:
            st.markdown("*No AI extracted information available*")

    # Display features in a nice grid layout
    features_to_display = []
    
    # Get features from description_analysis first
    description_analysis = property_details.get('description_analysis', {})
    if description_analysis.get('features'):
        features_to_display.extend(description_analysis['features'])
    
    # Add existing features if they exist and aren't already included
    if property_details.get('features'):
        for feature in property_details['features']:
            if feature not in features_to_display:
                features_to_display.append(feature)
    
    if features_to_display:
        st.markdown("#### Key Features")
        st.markdown("""
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
        """, unsafe_allow_html=True)
        
        # Create the feature grid
        features_html = '<div class="feature-grid">'
        for feature in features_to_display:
            features_html += f'<div class="feature-item">{feature}</div>'
        features_html += '</div>'
        
        st.markdown(features_html, unsafe_allow_html=True)

    # Display floorplan and EPC side by side in bordered boxes
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Floorplan")
        with st.container(border=True, height=500):
            st.markdown('<div class="bordered-box">', unsafe_allow_html=True)
            if property_details.get('floorplan'):
                try:
                    # Handle base64 string floorplan
                    floorplan_data = property_details['floorplan']
                    if isinstance(floorplan_data, str):
                        # Decode base64 string and display
                        decoded_floorplan = base64.b64decode(floorplan_data)
                        st.image(decoded_floorplan, caption="Floorplan", width=300)
                    else:
                        st.markdown("Ask agent for floorplan")
                except Exception as e:
                    st.markdown(f"Ask agent for floorplan")
                    print(f"Floorplan display error: {str(e)}")
            else:
                st.info("Ask Agent for floorplan")
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown("#### Energy Performance Certificate")
        with st.container(border=True, height=500):
            st.markdown('<div class="bordered-box">', unsafe_allow_html=True)
            if property_details.get('epc'):
                try:
                    # Handle both URL and base64 encoded images
                    if isinstance(property_details['epc'], str):
                        if property_details['epc'].startswith('data:image'):
                            # Handle base64 encoded image
                            st.image(property_details['epc'], caption="EPC Rating", width=300)
                        else:
                            # Handle URL
                            st.image(property_details['epc'], caption="EPC Rating", width=300)
                    else:
                        st.error("Invalid EPC image format")
                except Exception as e:
                    st.error(f"Error displaying EPC: {str(e)}")
                    print(f"EPC display error: {str(e)}")
            else:
                st.info("EPC not available")
            st.markdown('</div>', unsafe_allow_html=True)

def render_property_header(property_details, property_id):
    """Render the property header with title, price, bedrooms, and draft enquiry button."""
    # Property title
    st.title(property_details['address'])
    
    # Price, bedrooms, and draft enquiry button in the same row
    col1, col2, col3 = st.columns([5, 1, 1])
    
    with col1:
        st.markdown(f"### £{property_details['price']:,} | {property_details['num_bedrooms']} bedrooms")
    
    with col2:
        if st.button(
            "✉️ Draft enquiry",
            key=f"draft_enquiry_{property_id}",
            type="primary"
        ):
            # Generate draft message
            message = draft_enquiry(
                property_details=property_details,
                customer_name=st.session_state.get('first_name', 'Customer'),
            )
            # Store in session state
            st.session_state[f"draft_msg_{property_id}"] = message
            st.session_state[f"show_draft_{property_id}"] = True
    with col3:
        st.link_button(
            "View original",
            url=f"https://www.rightmove.co.uk/properties/{property_id}"
        )


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
        property_details = st.session_state.property_shortlist.get(int(property_id))
    
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

    # Render AI notes
    render_ai_notes(property_details)

    # Property details in tabs
    tab1, tab2 = st.tabs(["Property Details", "Location"])

    with tab1:
        render_property_details_tab(property_details)

    with tab2:
        render_location_tab(property_details)

    # with tab3:
    #     show_chat_interface()