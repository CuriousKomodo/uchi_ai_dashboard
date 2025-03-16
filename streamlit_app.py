import streamlit as st
from google.oauth2 import id_token
from google.auth.transport import requests
import json



# Streamlit UI
st.set_page_config(page_title="AI-Powered Real Estate Assistant", layout="wide")
st.title("🏡 AI-Powered Real Estate Assistant")

# Authentication (Simple Simulation)
user_email = st.text_input("Enter your email to log in:")
if user_email:
    st.success(f"Welcome {user_email}")

    # Fetch properties from Firestore
    st.subheader("🏠 Recommended Properties")
    properties_ref = db.collection("properties")
    properties = properties_ref.stream()

    for prop in properties:
        prop_data = prop.to_dict()
        st.write(f"**{prop_data['title']}** - {prop_data['price']}")
        st.image(prop_data['image_url'], width=300)

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"💾 Save {prop.id}"):
                db.collection("users").document(user_email).update(
                    {"saved_properties": firestore.ArrayUnion([prop.id])})
                st.success("Property saved!")

        with col2:
            if st.button(f"📅 Arrange Viewing {prop.id}"):
                db.collection("users").document(user_email).update(
                    {"viewing_requests": firestore.ArrayUnion([prop.id])})
                st.success("Viewing requested!")

    # Sidebar for user account settings
    st.sidebar.header("⚙️ Account Settings")
    st.sidebar.write("Update your details here.")
