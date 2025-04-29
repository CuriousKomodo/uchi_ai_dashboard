import streamlit as st
from connection.firestore import FireStore
from custom_exceptions import NoUserFound
from utils.draft import draft_enquiry
from utils.filter import sort_by_chosen_option
from utils.image_gallery_manager import ImageGalleryManager

def on_draft_enquiry(
        property_id: str,
        property_details: dict,
        customer_name: str,
        customer_intent: str = ""
):
    expander_key = f"expander_{property_id}"
    message = draft_enquiry(
        property_details=property_details,
        customer_name=customer_name,
        customer_intent=customer_intent,
    )

    # store your draft and expand flag in session_state
    st.session_state[f"draft_msg_{property_id}"] = message
    st.session_state[expander_key] = True

def login(firestore: FireStore):
    """Handle user login."""
    st.title("Log into Uchi Dashboard")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        try:
            user_details = firestore.fetch_user_details_by_email(email)
            if user_details.get("password") == password:
                st.session_state.authenticated = True
                st.session_state.email = email
                st.session_state.user_id = user_details.get("user_id")
                st.session_state.first_name = user_details.get("first_name")
                st.rerun()
            else:
                st.error("Invalid password")
        except NoUserFound:
            st.error("Email is not found. Please feel free to register.")

def show_dashboard(firestore: FireStore):
    """Show the main dashboard."""
    # Login check
    if not st.session_state.authenticated:
        login(firestore)
        return

    # Fetch properties from Firestore
    with st.spinner(f'Hello {st.session_state.first_name}. Loading properties for you...'):
        shortlist = firestore.get_shortlists_by_user_id(st.session_state.user_id)

    if shortlist:
        sort_by = st.selectbox(
            "Sort by",
            options=["Price: Low to High",
                     "Price: High to Low",
                     "Bedrooms: Most to Fewest",
                     "Commute time to work: Shortest to Longest",
                     "Criteria Match: Most to Least"
                     ],
            key="user_sort_order"
        )
        sort_by_chosen_option(sort_by, shortlist)

        # Initialize image gallery manager
        gallery_manager = ImageGalleryManager()
        gallery_manager.pre_decode_images(shortlist)

        for prop in shortlist:
            st.markdown("---")
            with st.container():
                col1, col2, col3, col4 = st.columns([5, 1, 2, 2])
                with col1:
                    st.markdown(f"<h3>{prop['address']}</h3>", unsafe_allow_html=True)
                    st.markdown(f"<h4>{prop['num_bedrooms']} bedrooms - £{prop['price']}</h4>", unsafe_allow_html=True)
                with col2:
                    if st.button(f"❤️ Save", key=f"save {prop['property_id']}"):
                        st.success("Property saved!")
                with col3:
                    enquiry_key = f"enquire_{prop['property_id']}"
                    if st.button(
                            "️✉️ Draft enquiry",
                            key=enquiry_key,
                            on_click=on_draft_enquiry,
                            args=(prop['property_id'], prop, st.session_state.first_name, "general enquiry")
                    ):
                        pass
                with col4:
                    if st.session_state.get(f"draft_msg_{prop['property_id']}", False):
                        with st.popover("📝Review your draft"):
                            st.markdown(
                                f"<h5>Subject: enquiring about property at {prop['address']}</h3>",
                                unsafe_allow_html=True
                            )
                            st.text_area(
                                f"Feel free to edit the content.",
                                value=st.session_state.get(f"draft_msg_{prop['property_id']}"),
                                height=300,
                                key=f"textarea_{prop['property_id']}"
                            )

            with st.container():
                col1, col2 = st.columns([3, 5])
                with col1:
                    gallery_manager.display_image_gallery(prop)
                    col11, col12, col13 = st.columns([1,1,1])
                    with col11:
                        st.link_button("View original", url=f"https://www.rightmove.co.uk/properties/{prop['property_id']}")
                    with col12:
                        # Use Streamlit's query parameters for chat URL
                        chat_params = {
                            "property_id": prop['property_id'],
                            "address": prop['address'],
                            "price": prop['price'],
                            "bedrooms": prop['num_bedrooms']
                        }
                        if st.button("🤖Ask AI", key=f"chat_{prop['property_id']}"):
                            st.query_params.update(**chat_params)
                            st.rerun()
                    with col13:
                        if prop.get('floorplans') and isinstance(prop["floorplans"], list):
                            floorplan_url = prop["floorplans"][0].get("url")
                            st.link_button("Floorplan", url=floorplan_url)

                with col2:
                    st.write("<h5>🏠Matched property criteria: </h5>", unsafe_allow_html=True)
                    match_criteria = prop.get("match_output", {})
                    match_criteria_additional = prop.get("matched_criteria", {})
                    match_criteria.update({criteria: True for criteria in match_criteria_additional})
                    match_criteria_string = ""  # widgets with colors
                    for key, value in match_criteria.items():
                        if isinstance(value, bool) and value:
                            match_criteria_string += f" {key.replace('_', ' ').capitalize()} ✅  "
                    st.markdown(match_criteria_string, unsafe_allow_html=True)

                    if "stations" in prop:
                            st.write("**🚉 Nearest Stations:**")
                            for station in prop["stations"]:
                                st.write(f"- {station['station']} ({station['distance']} miles)")

                    if prop["journey"] and prop["journey"].get("duration"):
                        st.markdown(
                            f"<h6>🚗Estimated commute to work: {prop['journey'].get('duration')} min </h6>",
                            unsafe_allow_html=True
                        )
                    if prop.get('deprivation') and prop["deprivation"] > 0:
                        st.markdown(f"<h6>% households with any deprivation: {prop.get('deprivation')}% <h6>",
                                    unsafe_allow_html=True)
                        if prop['deprivation'] < 20:
                            st.markdown(
                                "⭐Relatively wealthy area, i.e. fewer than 1 in 5 residents are income‑deprived.")

                    with st.expander("🏞️🧘Places within 1km which might be relevant", expanded=False):
                        st.markdown(
                            "<div style='min-width: 500px;'>", unsafe_allow_html=True
                        )
                        for place in prop.get("places_of_interest", []):
                            if place.get("rating"):
                                st.write(f"- {place['name']} (⭐ {place['rating']})")
                            else:
                                st.write(f"- {place['name']} ")
                        st.markdown("</div>", unsafe_allow_html=True)