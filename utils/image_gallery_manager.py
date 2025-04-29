import base64
import streamlit as st
from typing import Dict, List, Optional
import time


class ImageGalleryManager:
    def __init__(self):
        self.max_cache_size = 50  # Maximum number of images to cache
        self.cache_ttl = 3600  # Cache TTL in seconds

    def pre_decode_images(self, properties: List[Dict]):
        """Pre-decode images for a list of properties."""
        for prop in properties:
            property_id = prop.get('property_id')
            if not property_id:
                continue

            # Check if we need to clean up old cache entries
            self._cleanup_old_cache()

            # Only decode if not already in cache
            if property_id not in st.session_state.decoded_images:
                images = prop.get('property_details', {}).get('compressed_images', [])
                if images:
                    decoded_images = []
                    for img in images:
                        try:
                            decoded = base64.b64decode(img.get('url', ''))
                            decoded_images.append(decoded)
                        except Exception as e:
                            print(f"Error decoding image for property {property_id}: {str(e)}")
                    
                    if decoded_images:
                        st.session_state.decoded_images[property_id] = decoded_images
                        st.session_state.image_cache_timestamps[property_id] = time.time()

    def _cleanup_old_cache(self):
        """Clean up old cache entries based on TTL and size."""
        current_time = time.time()
        
        # Remove entries older than TTL
        expired_keys = [
            key for key, timestamp in st.session_state.image_cache_timestamps.items()
            if current_time - timestamp > self.cache_ttl
        ]
        
        for key in expired_keys:
            if key in st.session_state.decoded_images:
                del st.session_state.decoded_images[key]
            if key in st.session_state.image_cache_timestamps:
                del st.session_state.image_cache_timestamps[key]

        # If still too many entries, remove oldest
        if len(st.session_state.decoded_images) > self.max_cache_size:
            sorted_keys = sorted(
                st.session_state.image_cache_timestamps.keys(),
                key=lambda k: st.session_state.image_cache_timestamps[k]
            )
            for key in sorted_keys[:len(st.session_state.decoded_images) - self.max_cache_size]:
                if key in st.session_state.decoded_images:
                    del st.session_state.decoded_images[key]
                if key in st.session_state.image_cache_timestamps:
                    del st.session_state.image_cache_timestamps[key]

    def display_image_gallery(self, prop: Dict):
        """Display image gallery for a property."""
        property_id = prop.get('property_id')
        if not property_id:
            return

        # Initialize image index if not exists
        if f"image_index_{property_id}" not in st.session_state:
            st.session_state[f"image_index_{property_id}"] = 0

        # Get cached images or decode new ones
        if property_id in st.session_state.decoded_images:
            images = st.session_state.decoded_images[property_id]
        else:
            images = prop.get('property_details', {}).get('images', [])
            decoded_images = []
            for img in images:
                try:
                    decoded = base64.b64decode(img.get('url', ''))
                    decoded_images.append(decoded)
                except Exception as e:
                    print(f"Error decoding image for property {property_id}: {str(e)}")
            if decoded_images:
                st.session_state.decoded_images[property_id] = decoded_images
                st.session_state.image_cache_timestamps[property_id] = time.time()
                images = decoded_images

        if not images:
            st.write("No images available")
            return

        # Display current image
        current_index = st.session_state[f"image_index_{property_id}"]
        st.image(images[current_index], use_column_width=True)

        # Navigation buttons
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Previous", key=f"prev_{property_id}"):
                st.session_state[f"image_index_{property_id}"] = (current_index - 1) % len(images)
                st.rerun()
        with col2:
            if st.button("Next", key=f"next_{property_id}"):
                st.session_state[f"image_index_{property_id}"] = (current_index + 1) % len(images)
                st.rerun()