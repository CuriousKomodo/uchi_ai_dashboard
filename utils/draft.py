import os
from typing import Dict, Optional
import streamlit as st
import requests
from dotenv import load_dotenv

load_dotenv()

def draft_enquiry_using_endpoint(
        property_details: Dict,
        customer_name: str,
        customer_intent: Optional[str] = ""
):
    api_url = f'{os.getenv("UCHI_API_URL")}/draft_email'

    fields_to_exclude = ["journey", "matched_criteria", "places_of_interest", "image_analysis", "score", "stations", "extraction_id", "compressed_images"]
    property_details_trimmed = {k:v for k, v in property_details.items() if k not in fields_to_exclude}

    try:
        response = requests.post(
            url=api_url,
            json={
                "customer_name": customer_name,
                "property_details": property_details_trimmed,
                "customer_intention": customer_intent,
                }
        )
        if response.status_code == 200:
            return response.json()["message"]

    except requests.RequestException as e:
        default_message = f"Hi, \n I am interested in this property and would like to request for a viewing. Best, \n{customer_name}"
        return default_message


def draft_enquiry(
        property_details: Dict,
        customer_name: str,
):
    if property_details.get("draft"):
        draft = property_details.get("draft").replace("uchi_user", customer_name)
    else:
        draft = f"Hi I am interested in this property and would like to request for a viewing. Best, {customer_name}"
    return draft

def create_copy_button(text_to_copy):
    button_id = "copyButton" + text_to_copy

    button_html = f"""<button id="{button_id}">Copy</button>
    <script>
    document.getElementById("{button_id}").onclick = function() {{
        navigator.clipboard.writeText("{text_to_copy}").then(function() {{
            console.log('Async: Copying to clipboard was successful!');
        }}, function(err) {{
            console.error('Async: Could not copy text: ', err);
        }});
    }}
    </script>"""

    st.markdown(button_html, unsafe_allow_html=True)


def on_draft_enquiry(
        property_id: str,
        property_details: Dict,
        customer_name: str,
        customer_intent: Optional[str] = ""
):
    expander_key = f"expander_{property_id}"
    # message = draft_enquiry(
    #     property_details=property_details,
    #     customer_name=customer_name,
    #     customer_intent=customer_intent,
    # )
    message = "GENERAL ENQUIRY"

    # store your draft and expand flag in session_state
    st.session_state[f"draft_msg_{property_id}"] = message
    st.session_state[expander_key] = True

    # Show the expander if the flag is set in session state
    if st.session_state.get(expander_key, False):
        with st.expander("Edit your enquiry", expanded=True):
            edited_message = st.text_area(
                message,
                value=st.session_state.get(f"draft_msg_{property_id}", ""),
                height=300,
                key=f"textarea_{property_id}"
            )
            create_copy_button(edited_message)
            # Optionally, add a submit button here
            # if st.button("Submit Enquiry", key=f"submit_{prop['property_id']}"):
            #     st.success("Your enquiry has been submitted!")


if __name__ == "__main__":
    draft_enquiry(
        property_details={},
        customer_name="Kefei",
        customer_intent="I want to book viewing",
    )