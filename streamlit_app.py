import base64

import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
import json

from utils import read_json

# Streamlit UI
st.set_page_config(page_title="AI-Powered Real Estate Assistant", layout="wide")
st.title("🏡 AI-Powered Real Estate Assistant")

# Authentication (Simple Simulation)
# if "user_email" not in st.session_state:
#     user_email = st.text_input("Enter your email to log in:")
#     if user_email:
#         st.session_state.user_email = user_email
#
# else:
#     user_email = st.session_state.user_email
#     st.success(f"Welcome {user_email}")
# Fetch properties from Firestore
st.subheader("🏠 Recommended Properties")
# shortlist = shortlist_doc.to_dict().get("properties", [])
shortlist = read_json("cache/shortlist.json")
if shortlist:
    for prop in shortlist:
        st.markdown("---")  # Adds a separator between properties
        with st.container():
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"<h3>{prop['address']} - £{prop['price']}</h3>", unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
            with col2:
                if st.button(f"❤️ Save", key=f"save {prop['property_id']}"):
                    # db.collection("users").document(user_email).update(
                    #     {"saved_properties": firestore.ArrayUnion([prop['property_id']])})
                    st.success("Property saved!")
        with st.container():
            col1, col2 = st.columns([1, 2])
            # Display a single image on the left
            with col1:
                if prop.get("compressed_images"):
                    if f"img_index_{prop['property_id']}" not in st.session_state:
                        st.session_state[f"img_index_{prop['property_id']}"] = 0

                    img_index = st.session_state[f"img_index_{prop['property_id']}"]
                    img_data = base64.b64decode(prop["compressed_images"][img_index])
                    st.image(img_data, use_column_width=True)

                    col_img1, col_img2, col_img3 = st.columns([1,1,1])
                    with col_img1:
                        if st.button("⬅️prev", key=f" Previous {prop['property_id']}") and img_index > 0:
                            st.session_state[f"img_index_{prop['property_id']}"] -= 1
                            st.rerun()
                    with col_img3:
                        if st.button("next ➡️", key=f"️ Next {prop['property_id']}") and img_index < len(
                                prop["compressed_images"]) - 1:
                            st.session_state[f"img_index_{prop['property_id']}"] += 1
                            st.rerun()
                    with col_img2:
                        pass

                if "stations" in prop:
                    st.write("**🚉 Nearest Stations:**")
                    for station in prop["stations"]:
                        st.write(f"- {station['station']} ({station['distance']} miles)")


            # Display property details on the right
            with col2:
                st.write("<h5>🏠Matched property criteria: </h5>", unsafe_allow_html=True)
                match_criteria = prop.get("match_output", {})
                match_criteria_string = ""
                for key, value in match_criteria.items():
                    if isinstance(value, bool) and value:
                        match_criteria_string += f" {key.replace('_', ' ').capitalize()} ✅  "
                st.markdown(match_criteria_string, unsafe_allow_html=True)

                st.markdown("<h5>🤖Agent notes:</h5>", unsafe_allow_html=True)
                st.write(f"{prop['match_output']['reason']}")

                st.markdown("<h6>🚗Estimated commute to Liverpool Street = 50min</h6>", unsafe_allow_html=True)

                with st.expander("🕵️Neighborhood intelligence", expanded=False):
                    st.markdown(
                        "<div style='min-width: 500px;'>", unsafe_allow_html=True
                    )
                    st.write(f"% households with any deprivation: {prop.get('deprivation')}")

                    st.write("🏞️🧘Interesting places to visit within 1km")
                    for place in prop.get("places_of_interest", []):
                        st.write(f"- {place['name']} (⭐ {place['rating']})")
                    st.markdown("</div>", unsafe_allow_html=True)

else:
    print("No shortlist is found")

# Sidebar for user account settings
st.sidebar.header("⚙️ Account Settings")
st.sidebar.write("Update your details here.")
