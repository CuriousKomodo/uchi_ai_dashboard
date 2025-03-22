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
user_email = st.text_input("Enter your email to log in:")
if user_email:
    st.success(f"Welcome {user_email}")

    # Fetch properties from Firestore
    st.subheader("🏠 Recommended Properties")
    # shortlist = shortlist_doc.to_dict().get("properties", [])
    shortlist = read_json("cache/shortlist.json")
    for prop in shortlist:
        st.markdown("---")  # Adds a separator between properties
        with st.container():
            col1, col2 = st.columns([1, 2])

            # Display a single image on the left
            with col1:
                if prop.get("compressed_images"):
                    img_data = base64.b64decode(prop["compressed_images"][0])
                    st.image(img_data, use_column_width=True)

            # Display match criteria and places of interest on the right
            with col2:
                st.markdown(
                    f"""
                        <div style="border: 2px solid #ddd; padding: 15px; border-radius: 10px;">
                            <h4>{prop['address']} - £{prop['price']}</h4>
                        """,
                    unsafe_allow_html=True,
                )

                # Match criteria with ✅ emoji
                match_criteria = prop.get("match_output", {})
                for key, value in match_criteria.items():
                    if isinstance(value, bool) and value:
                        st.write(f"✅ {key.replace('_', ' ').capitalize()}")

                # Places of Interest
                st.write("**Nearby Places of Interest:**")
                for place in prop.get("places_of_interest", []):
                    st.write(f"- {place['name']} (⭐ {place['rating']})")

                # Save and Viewing Buttons
                col3, col4 = st.columns(2)
                with col3:
                    if st.button(f"💾 Save {prop['property_id']}"):
                        # db.collection("users").document(user_email).update(
                        #     {"saved_properties": firestore.ArrayUnion([prop['property_id']])})
                        st.success("Property saved!")
                with col4:
                    if st.button(f"📅 Arrange Viewing {prop['property_id']}"):
                        # db.collection("users").document(user_email).update(
                        #     {"viewing_requests": firestore.ArrayUnion([prop['property_id']])})
                        st.success("Viewing requested!")

                st.markdown("</div>", unsafe_allow_html=True)
else:
    st.warning("No shortlisted properties found.")

# Sidebar for user account settings
st.sidebar.header("⚙️ Account Settings")
st.sidebar.write("Update your details here.")
