import re
from math import radians, sin, cos, sqrt, atan2
from pathlib import Path
import pandas as pd


current_dir = Path(__file__).parent
root_dir = current_dir.parent.parent
schools_file = root_dir / "data" / "schools.pkl"
schools = pd.read_pickle(schools_file)

def extract_prefix_postcode(address):
    """Extract postcode from address string."""
    # Common UK postcode pattern
    try:
        partial_postcode = address.split(" ")[0]
        return partial_postcode
    except IndexError:
        print("cannot extract postcode")
        return ""

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula.
    
    Args:
        lat1 (float): Latitude of first point in degrees
        lon1 (float): Longitude of first point in degrees
        lat2 (float): Latitude of second point in degrees
        lon2 (float): Longitude of second point in degrees
        
    Returns:
        float: Distance between points in kilometers
    """
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = R * c

    return round(distance, 2)  # Round to 2 decimal places for readability

def get_nearby_schools(postcode_prefix, property_lat, property_lon, max_distance=2):
    """Get schools within max_distance km of the property."""
    # Calculate distances and filter schools
    schools_in_same_district = schools[schools['postcode'].str.startswith(f"{postcode_prefix}")]
    nearby_schools = []
    print("Number of schools in same district:", len(schools_in_same_district))
    for idx, school in schools_in_same_district.iterrows():
        if ('lat' in school) and ('lng' in school):
            distance = calculate_distance(
                property_lat, property_lon,
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
