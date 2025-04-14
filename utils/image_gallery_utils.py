import base64
import time
from typing import Dict, List, Optional
import streamlit as st

# Constants for cache management
MAX_CACHED_PROPERTIES = 10  # Maximum number of properties to cache
CACHE_CLEANUP_THRESHOLD = 15  # Cleanup when this many properties are cached

class ImageGalleryManager:
    def __init__(self):
        """Initialize the image gallery manager."""
        # Initialize session state for image indices and decoded images if not exists
        if "image_indices" not in st.session_state:
            st.session_state.image_indices = {}
        if "decoded_images" not in st.session_state:
            st.session_state.decoded_images = {}
        if "last_access_time" not in st.session_state:
            st.session_state.last_access_time = {}

    def cleanup_old_caches(self):
        """Clean up old caches when we exceed the threshold."""
        if len(st.session_state.decoded_images) > CACHE_CLEANUP_THRESHOLD:
            # Sort properties by last access time
            sorted_properties = sorted(
                st.session_state.last_access_time.items(),
                key=lambda x: x[1]
            )
            
            # Remove oldest caches until we're under the limit
            for property_id, _ in sorted_properties:
                if len(st.session_state.decoded_images) <= MAX_CACHED_PROPERTIES:
                    break
                if property_id in st.session_state.decoded_images:
                    del st.session_state.decoded_images[property_id]
                    del st.session_state.image_indices[property_id]
                    del st.session_state.last_access_time[property_id]

    def update_cache_access_time(self, property_id: str):
        """Update the last access time for a property's cache."""
        st.session_state.last_access_time[property_id] = time.time()

    def decode_images(self, property_id: str, compressed_images: List[str]) -> bool:
        """Decode and cache images for a property."""
        try:
            st.session_state.decoded_images[property_id] = [
                base64.b64decode(img) for img in compressed_images
            ]
            return True
        except Exception as e:
            st.error(f"Error decoding images: {str(e)}")
            return False

    def get_current_image(self, property_id: str) -> Optional[bytes]:
        """Get the current image for a property."""
        try:
            return st.session_state.decoded_images[property_id][st.session_state.image_indices[property_id]]
        except (KeyError, IndexError):
            return None

    def navigate_image(self, property_id: str, direction: str) -> bool:
        """
        Navigate to next/previous image.
        
        Args:
            property_id: The ID of the property
            direction: Either 'next' or 'prev'
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            current_index = st.session_state.image_indices[property_id]
            max_index = len(st.session_state.decoded_images[property_id]) - 1
            
            if direction == 'next' and current_index < max_index:
                st.session_state.image_indices[property_id] += 1
                return True
            elif direction == 'prev' and current_index > 0:
                st.session_state.image_indices[property_id] -= 1
                return True
            return False
        except (KeyError, IndexError):
            return False

    def display_image_gallery(self, prop: Dict) -> None:
        """
        Display the image gallery for a property.
        
        Args:
            prop: The property dictionary containing images and metadata
        """
        if not prop.get("compressed_images"):
            return

        property_id = prop['property_id']
        
        # Update last access time
        self.update_cache_access_time(property_id)
        
        # Initialize image index if not exists
        if property_id not in st.session_state.image_indices:
            st.session_state.image_indices[property_id] = 0
            # Pre-decode all images for this property
            if not self.decode_images(property_id, prop["compressed_images"]):
                return

        # Create a container for the image gallery
        image_container = st.container()
        
        # Display current image
        with image_container:
            current_image = self.get_current_image(property_id)
            if current_image:
                try:
                    st.image(current_image, use_column_width=True)
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")

        # Navigation buttons
        col_img1, col_img2, col_img3 = st.columns([1,1,1])
        with col_img1:
            if st.button("⬅️prev", key=f"prev_{property_id}"):
                if self.navigate_image(property_id, 'prev'):
                    self.update_cache_access_time(property_id)
                    with image_container:
                        current_image = self.get_current_image(property_id)
                        if current_image:
                            st.image(current_image, use_column_width=True)
        with col_img3:
            if st.button("next ➡️", key=f"next_{property_id}"):
                if self.navigate_image(property_id, 'next'):
                    self.update_cache_access_time(property_id)
                    with image_container:
                        current_image = self.get_current_image(property_id)
                        if current_image:
                            st.image(current_image, use_column_width=True)
        with col_img2:
            st.write(f"Image {st.session_state.image_indices[property_id] + 1} of {len(prop['compressed_images'])}") 