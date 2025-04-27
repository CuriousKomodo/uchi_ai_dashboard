import os
from typing import Dict, Optional

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def draft_enquiry(
        property_details: Dict,
        customer_name: str,
        customer_intent: Optional[str] = ""
):
    api_url = os.getenv("UCHI_API_URL")

    try:
        response = requests.post(api_url, json={
            "customer_name": customer_name,
            "property_details": property_details,
            "customer_intent": customer_intent,
        })
        response.raise_for_status()  # Raise error if not 200

        draft_message = response.json().get("message", "Something went wrong")

        # Open a modal popup with editable text area
        with st.modal("Edit your enquiry"):
            edited_message = st.text_area(
                "Your draft:",
                value=draft_message,
                height=300
            )
            # if st.button("Submit Enquiry"):
            #     st.success("Your enquiry has been submitted!")

    except requests.RequestException as e:
        st.error(f"Failed to get draft message: {e}")
