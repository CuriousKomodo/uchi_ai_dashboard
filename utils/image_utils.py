import base64
import streamlit as st
from typing import List, Dict, Optional


def decode_image(image_data: Dict) -> Optional[bytes]:
    """Decode a single image from base64 data."""
    try:
        return base64.b64decode(image_data["base64"])
    except Exception as e:
        print(f"Error decoding image: {str(e)}")
        return None


def decode_images_sequential(compressed_images: List[Dict], property_id: str) -> None:
    """Decode all images for a property sequentially and cache them in session state."""
    for idx, image_data in enumerate(compressed_images):
        cache_key = f"img_{property_id}_{idx}"
        if cache_key not in st.session_state:
            try:
                decoded_image = decode_image(image_data)
                if decoded_image:
                    st.session_state[cache_key] = decoded_image
            except Exception as e:
                print(f"Error processing image {idx} for property {property_id}: {str(e)}")


def display_image_grid(compressed_images: List[Dict], property_id: str, rows: int = 2, cols: int = 4) -> None:
    """Display images in a grid layout."""
    for row in range(rows):
        st_cols = st.columns(cols)
        for col in range(cols):
            idx = row * cols + col
            if idx < len(compressed_images):
                cache_key = f"img_{property_id}_{idx}"
                if cache_key in st.session_state:
                    with st_cols[col]:
                        st.image(
                            st.session_state[cache_key],
                            use_column_width=True
                        )


def render_property_images(property_details: Dict, property_id: str) -> None:
    """Render property images in a 2x4 grid with sequential decoding."""
    if property_details.get('compressed_images'):
        # Check if the first image is already cached (indicates all images are likely cached)
        first_image_cache_key = f"img_{property_id}_0"
        
        # Only decode if the first image is not cached
        if first_image_cache_key not in st.session_state:
            decode_images_sequential(property_details['compressed_images'], property_id)
        
        # Display images in grid
        display_image_grid(property_details['compressed_images'], property_id) 