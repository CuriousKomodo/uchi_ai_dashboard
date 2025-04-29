import streamlit as st
import requests
from typing import Dict

def get_property_context() -> Dict:
    """Get property context from URL parameters."""
    query_params = st.query_params
    return {
        "property_id": query_params.get("property_id", [""])[0],
        "address": query_params.get("address", [""])[0],
        "price": query_params.get("price", [""])[0],
        "bedrooms": query_params.get("bedrooms", [""])[0]
    }

def get_chat_response(messages: list, property_context: Dict) -> str:
    """Get response from the chat API."""
    try:
        response = requests.post(
            f"{st.secrets['UCHI_API_URL']}/chat",
            json={
                "messages": messages,
                "property_context": property_context
            }
        )
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return "Sorry, I'm having trouble connecting to the chat service. Please try again later."
    except Exception as e:
        st.error(f"Error connecting to chat service: {str(e)}")
        return "Sorry, I'm having trouble connecting to the chat service. Please try again later."

def show_chat_interface():
    """Show the chat interface."""
    property_context = get_property_context()
    
    # Display property info
    st.title("🤖 AI Property Assistant")
    st.markdown(f"### {property_context['address']}")
    st.markdown(f"**Price:** £{property_context['price']} | **Bedrooms:** {property_context['bedrooms']}")
    st.markdown("---")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": f"Hello! I'm your AI assistant for the property at {property_context['address']}. How can I help you today?"
            }
        ]

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask me anything about this property..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            response = get_chat_response(st.session_state.messages, property_context)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

    # Back to dashboard button
    if st.button("← Back to Dashboard"):
        st.query_params.clear() 