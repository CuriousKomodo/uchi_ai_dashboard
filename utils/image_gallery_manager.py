import base64
from typing import Dict, List
import streamlit as st


class ImageGalleryManager:
    def __init__(self):
        """Initialize the image gallery manager."""
        if "image_indices" not in st.session_state:
            st.session_state.image_indices = {}
        if "decoded_images" not in st.session_state:
            st.session_state.decoded_images = {}

    def pre_decode_images(self, properties: List[Dict]) -> None:
        """
        Pre-decode all images for all properties.

        Args:
            properties: List of property dictionaries containing images
        """
        for prop in properties:
            if not prop.get("compressed_images"):
                continue

            property_id = prop['property_id']
            try:
                st.session_state.decoded_images[property_id] = [
                    base64.b64decode(img) for img in prop["compressed_images"]
                ]
            except Exception as e:
                st.error(f"Error decoding images for property {property_id}: {str(e)}")

    def display_image_gallery(self, prop: Dict) -> None:
        """
        Display the image gallery for a property.

        Args:
            prop: The property dictionary containing images and metadata
        """
        if not prop.get("compressed_images"):
            return

        property_id = prop['property_id']

        # Initialize or get current image index
        if property_id not in st.session_state.image_indices:
            st.session_state.image_indices[property_id] = 0

        # Get current image from pre-decoded images
        try:
            current_image = st.session_state.decoded_images[property_id][st.session_state.image_indices[property_id]]
            st.image(current_image, use_column_width=True)
        except Exception as e:
            st.error(f"Error displaying image: {str(e)}")
            return

        # Navigation buttons
        col_img1, col_img2, col_img3 = st.columns([1, 1, 1])
        with col_img1:
            if st.button("⬅️prev", key=f"prev_{property_id}"):
                if st.session_state.image_indices[property_id] > 0:
                    st.session_state.image_indices[property_id] -= 1
                    # st.rerun()
        with col_img3:
            if st.button("next ➡️", key=f"next_{property_id}"):
                if st.session_state.image_indices[property_id] < len(prop["compressed_images"]) - 1:
                    st.session_state.image_indices[property_id] += 1
                    # st.rerun()
        with col_img2:
            st.write(f"Image {st.session_state.image_indices[property_id] + 1} of {len(prop['compressed_images'])}")