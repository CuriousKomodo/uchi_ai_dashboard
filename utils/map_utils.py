import folium
from utils.location_utils import extract_coordinates_from_place_uri, geocode_address
from utils.place_utils import get_place_icon_and_color

def add_property_marker(map_obj, latitude, longitude, address):
    """Add property marker to the map."""
    folium.Marker(
        [latitude, longitude],
        popup=address,
        icon=folium.Icon(color='red', icon='home', prefix='fa')
    ).add_to(map_obj)


def add_school_markers(map_obj, schools):
    """Add school markers to the map."""
    for school in schools:
        # Try to get coordinates - check if they exist in the school data
        school_lat = school.get('lat') or school.get('latitude')
        school_lng = school.get('lng') or school.get('longitude')
        
        # If no coordinates, try geocoding the address
        if school_lat is None or school_lng is None:
            if school.get('address'):
                school_lat, school_lng = geocode_address(school['address'])
        
        # Only add marker if we have coordinates
        if school_lat is not None and school_lng is not None:
            popup_content = f"""
                <div style='min-width: 200px'>
                    <h4 style='margin: 0 0 5px 0'>{school.get('name', 'Unknown School')}</h4>
                    <p style='margin: 0 0 5px 0'>
                        <strong>Distance:</strong> {school.get('distance', 'N/A')} km<br>
                        <strong>Rating:</strong> {school.get('rating', 'N/A')}
                    </p>
                    {f"<a href='{school['url']}' target='_blank' style='color: #0066cc; text-decoration: none;'>View School Website</a>" if school.get('url') else ''}
                </div>
            """

            folium.Marker(
                [float(school_lat), float(school_lng)],
                popup=folium.Popup(popup_content, max_width=300),
                icon=folium.Icon(color='blue', icon='graduation-cap', prefix='fa')
            ).add_to(map_obj)


def add_supermarket_markers(map_obj, supermarkets):
    """Add supermarket markers to the map."""
    for supermarket in supermarkets:
        # Try to get coordinates from place_uri first
        lat, lng = extract_coordinates_from_place_uri(supermarket.get('place_uri', ''))

        # If no coordinates from URI, try geocoding the address
        if lat is None or lng is None:
            lat, lng = geocode_address(supermarket.get('address', ''))

        # Only add marker if we have coordinates
        if lat is not None and lng is not None:
            popup_content = f"""
                <div style='min-width: 250px; max-width: 300px;'>
                    <h4 style='margin: 0 0 10px 0; color: #2E8B57;'>{supermarket['name']}</h4>
                    <p style='margin: 0 0 5px 0;'>
                        <strong>Rating:</strong> ⭐ {supermarket.get('rating', 'N/A')}<br>
                        <strong>Address:</strong> {supermarket.get('address', 'N/A')}
                    </p>
                    {f"<a href='{supermarket['place_uri']}' target='_blank' style='color: #0066cc; text-decoration: none;'>View on Google Maps</a>" if supermarket.get('place_uri') else ''}
                </div>
            """

            folium.Marker(
                [lat, lng],
                popup=folium.Popup(popup_content, max_width=350),
                icon=folium.Icon(color='green', icon='shopping-cart', prefix='fa')
            ).add_to(map_obj)


def add_green_space_markers(map_obj, green_spaces):
    """Add green space markers to the map."""
    for green_space in green_spaces:
        # Try to get coordinates from place_uri first
        lat, lng = extract_coordinates_from_place_uri(green_space.get('place_uri', ''))

        # If no coordinates from URI, try geocoding the address
        if lat is None or lng is None:
            lat, lng = geocode_address(green_space.get('address', ''))

        # Only add marker if we have coordinates
        if lat is not None and lng is not None:
            popup_content = f"""
                <div style='min-width: 250px; max-width: 300px;'>
                    <h4 style='margin: 0 0 10px 0; color: #228B22;'>{green_space['name']}</h4>
                    <p style='margin: 0 0 5px 0;'>
                        {f"<strong>Rating:</strong> ⭐ {green_space['rating']}<br>" if green_space.get('rating') else ''}
                        {f"<strong>Type:</strong> {', '.join(green_space['types'][:2])}<br>" if green_space.get('types') else ''}
                        <strong>Address:</strong> {green_space.get('address', 'N/A')}
                    </p>
                    {f"<a href='{green_space['place_uri']}' target='_blank' style='color: #0066cc; text-decoration: none;'>View on Google Maps</a>" if green_space.get('place_uri') else ''}
                </div>
            """

            folium.Marker(
                [lat, lng],
                popup=folium.Popup(popup_content, max_width=350),
                icon=folium.Icon(color='darkgreen', icon='tree', prefix='fa')
            ).add_to(map_obj)


def add_places_of_interest_markers(map_obj, places_of_interest):
    """Add places of interest markers to the map."""
    for place in places_of_interest:
        # Try to get coordinates from place_uri first
        lat, lng = extract_coordinates_from_place_uri(place.get('place_uri', ''))

        # If no coordinates from URI, try geocoding the address
        if lat is None or lng is None:
            lat, lng = geocode_address(place.get('address', ''))

        # Only add marker if we have coordinates
        if lat is not None and lng is not None:
            # Determine icon and color based on place type
            icon_name, icon_color = get_place_icon_and_color(place.get('types', []))
            
            popup_content = f"""
                <div style='min-width: 250px; max-width: 300px;'>
                    <h4 style='margin: 0 0 10px 0; color: {icon_color};'>{place['name']}</h4>
                    <p style='margin: 0 0 5px 0;'>
                        {f"<strong>Rating:</strong> ⭐ {place['rating']}<br>" if place.get('rating') else ''}
                        {f"<strong>Type:</strong> {', '.join(place['types'][:2])}<br>" if place.get('types') else ''}
                        {f"<strong>Address:</strong> {place['address']}<br>" if place.get('address') else ''}
                    </p>
                    {f"<a href='{place['place_uri']}' target='_blank' style='color: #0066cc; text-decoration: none;'>View on Google Maps</a>" if place.get('place_uri') else ''}
                </div>
            """

            folium.Marker(
                [lat, lng],
                popup=folium.Popup(popup_content, max_width=350),
                icon=folium.Icon(color=icon_color, icon=icon_name, prefix='fa')
            ).add_to(map_obj)


def create_property_map(property_details):
    """Create and return a folium map with all markers."""
    # Create map centered on property location or central London
    latitude = property_details.get('latitude')
    longitude = property_details.get('longitude')
    if not (isinstance(latitude, float) and isinstance(longitude, float)):
        latitude, longitude = 51.5074, -0.1278
        
    # Create the map
    m = folium.Map(location=[latitude, longitude], zoom_start=15)
    
    # Add property marker
    add_property_marker(m, latitude, longitude, property_details['address'])
    
    # Add nearby amenities
    neighborhood_info = property_details.get("neighborhood_info", {})
    nearby_schools = neighborhood_info.get("nearby_schools", [])
    nearby_supermarkets = neighborhood_info.get("nearby_supermarkets", [])
    nearby_green_spaces = neighborhood_info.get("nearby_green_spaces", [])
    
    add_school_markers(m, nearby_schools)
    add_supermarket_markers(m, nearby_supermarkets)
    add_green_space_markers(m, nearby_green_spaces)
    
    # Add places of interest
    places_of_interest = property_details.get("places_of_interest", [])
    add_places_of_interest_markers(m, places_of_interest)
    
    return m