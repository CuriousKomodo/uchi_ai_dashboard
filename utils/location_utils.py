import re
from math import radians, sin, cos, sqrt, atan2, asin
from pathlib import Path
import pandas as pd
import requests
import time


current_dir = Path(__file__).parent
root_dir = current_dir.parent
schools_file = root_dir / "data" / "schools.pkl"
schools = pd.read_pickle(schools_file)

def extract_prefix_postcode(postcode):
    """Extract the prefix from a postcode (e.g., 'SW1A' from 'SW1A 1AA')."""
    if not postcode:
        return ""
    # Extract the letters and first digit(s) before the space
    match = re.match(r'^([A-Z]{1,2}\d{1,2}[A-Z]?)', postcode.upper().replace(' ', ''))
    return match.group(1) if match else postcode.split()[0] if ' ' in postcode else postcode

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two points using the Haversine formula."""
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r

def get_nearby_schools(postcode_prefix, property_lat, property_lng, max_distance=2):
    """Get schools within max_distance km of the property."""
    # Calculate distances and filter schools
    schools_in_same_district = schools[schools['postcode'].str.startswith(f"{postcode_prefix}")]
    nearby_schools = []
    print("Number of schools in same district:", len(schools_in_same_district))
    for idx, school in schools_in_same_district.iterrows():
        if ('lat' in school) and ('lng' in school):
            distance = calculate_distance(
                property_lat, property_lng,
                float(school['lat']), float(school['lng'])
            )
            if distance <= max_distance:
                school['distance'] = round(distance, 2)
                nearby_schools.append(school)
        else:
            school['distance'] = max_distance
            nearby_schools.append(school)  # Just display the school anyway
    
    # Sort first by whether school is outstanding, then by distance
    return sorted(nearby_schools, key=lambda x: (
        str(x.get('rating', '')).lower() != 'outstanding',  # False (0) for outstanding comes first
        x['distance']  # Then sort by distance
    ))

def extract_coordinates_from_place_uri(place_uri):
    """Extract coordinates from a Google Maps place URI."""
    if not place_uri:
        return None, None
    
    # Look for coordinates in the format @lat,lng
    coord_pattern = r'@(-?\d+\.\d+),(-?\d+\.\d+)'
    match = re.search(coord_pattern, place_uri)
    
    if match:
        lat, lng = float(match.group(1)), float(match.group(2))
        return lat, lng
    
    return None, None

def geocode_address(address):
    """Geocode an address using OpenStreetMap's Nominatim service."""
    if not address:
        return None, None
    
    try:
        # Use Nominatim API for geocoding
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'PropertyDashboard/1.0'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lng = float(data[0]['lon'])
            return lat, lng
        
    except Exception as e:
        print(f"Geocoding error for address '{address}': {str(e)}")
    
    return None, None


if __name__ == "__main__":
    print(extract_coordinates_from_place_uri("https://www.google.com/maps/place//data=!3m4!1e2!3m2!1sCIHM0ogKEICAgID28_2DIg!2e10!4m2!3m1!1s0x48762142bb7098ed:0x9a17f2df4ea5f2fc"))