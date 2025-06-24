def get_place_icon_and_color(types):
    """Get appropriate icon and color based on place types."""
    if not types:
        return 'map-marker', 'gray'
    
    types_lower = [t.lower() for t in types]
    
    # Restaurant and food
    if any(t in types_lower for t in ['restaurant', 'food', 'cafe', 'bar', 'bakery', 'pizza', 'takeaway']):
        return 'utensils', 'orange'
    
    # Shopping
    if any(t in types_lower for t in ['store', 'shopping', 'retail', 'clothing', 'jewelry', 'electronics']):
        return 'shopping-bag', 'purple'
    
    # Entertainment
    if any(t in types_lower for t in ['movie', 'theater', 'cinema', 'entertainment', 'nightclub', 'casino']):
        return 'film', 'darkred'
    
    # Sports and fitness
    if any(t in types_lower for t in ['gym', 'fitness', 'sports', 'stadium', 'swimming', 'tennis']):
        return 'dumbbell', 'darkblue'
    
    # Healthcare
    if any(t in types_lower for t in ['hospital', 'pharmacy', 'doctor', 'health', 'dentist', 'clinic']):
        return 'medkit', 'red'
    
    # Transport
    if any(t in types_lower for t in ['transit', 'bus', 'train', 'subway', 'taxi', 'car_rental']):
        return 'bus', 'darkgreen'
    
    # Cultural
    if any(t in types_lower for t in ['museum', 'library', 'art', 'cultural', 'gallery', 'theater']):
        return 'landmark', 'cadetblue'
    
    # Religious
    if any(t in types_lower for t in ['church', 'mosque', 'temple', 'synagogue', 'place_of_worship']):
        return 'pray', 'saddlebrown'
    
    # Banking and Finance
    if any(t in types_lower for t in ['bank', 'atm', 'finance', 'insurance']):
        return 'university', 'darkgreen'
    
    # Post Office and Services
    if any(t in types_lower for t in ['post_office', 'mail', 'postal']):
        return 'envelope', 'navy'
    
    # Childcare and Education
    if any(t in types_lower for t in ['childcare', 'daycare', 'nursery', 'kindergarten']):
        return 'baby', 'pink'
    
    # Beauty and Personal Care
    if any(t in types_lower for t in ['beauty_salon', 'hair_care', 'spa', 'nail_salon']):
        return 'cut', 'hotpink'
    
    # Automotive
    if any(t in types_lower for t in ['car_dealer', 'car_repair', 'gas_station', 'parking']):
        return 'car', 'black'
    
    # Home and Garden
    if any(t in types_lower for t in ['hardware_store', 'garden_center', 'furniture_store']):
        return 'home', 'olive'
    
    # Default
    return 'map-marker', 'gray'


def get_place_emoji(types):
    """Get appropriate emoji based on place types."""
    if not types:
        return "📍"
    
    types_lower = [t.lower() for t in types]
    
    # Restaurant and food
    if any(t in types_lower for t in ['restaurant', 'food', 'cafe', 'bar', 'bakery', 'pizza', 'takeaway']):
        return "🍽️"
    
    # Shopping
    if any(t in types_lower for t in ['store', 'shopping', 'retail', 'clothing', 'jewelry', 'electronics']):
        return "🛍️"
    
    # Entertainment
    if any(t in types_lower for t in ['movie', 'theater', 'cinema', 'entertainment', 'nightclub', 'casino']):
        return "🎬"
    
    # Sports and fitness
    if any(t in types_lower for t in ['gym', 'fitness', 'sports', 'stadium', 'swimming', 'tennis']):
        return "💪"
    
    # Healthcare
    if any(t in types_lower for t in ['hospital', 'pharmacy', 'doctor', 'health', 'dentist', 'clinic']):
        return "🏥"
    
    # Transport
    if any(t in types_lower for t in ['transit', 'bus', 'train', 'subway', 'taxi', 'car_rental']):
        return "🚌"
    
    # Cultural
    if any(t in types_lower for t in ['museum', 'library', 'art', 'cultural', 'gallery', 'theater']):
        return "🏛️"
    
    # Religious
    if any(t in types_lower for t in ['church', 'mosque', 'temple', 'synagogue', 'place_of_worship']):
        return "🙏"
    
    # Banking and Finance
    if any(t in types_lower for t in ['bank', 'atm', 'finance', 'insurance']):
        return "🏦"
    
    # Post Office and Services
    if any(t in types_lower for t in ['post_office', 'mail', 'postal']):
        return "📮"
    
    # Childcare and Education
    if any(t in types_lower for t in ['childcare', 'daycare', 'nursery', 'kindergarten']):
        return "👶"
    
    # Beauty and Personal Care
    if any(t in types_lower for t in ['beauty_salon', 'hair_care', 'spa', 'nail_salon']):
        return "💇‍♀️"
    
    # Automotive
    if any(t in types_lower for t in ['car_dealer', 'car_repair', 'gas_station', 'parking']):
        return "🚗"
    
    # Home and Garden
    if any(t in types_lower for t in ['hardware_store', 'garden_center', 'furniture_store']):
        return "🔨"
    
    # Default
    return "📍"


def get_place_category(types):
    """Get the category name for a place based on its types."""
    if not types:
        return "Other"
    
    types_lower = [t.lower() for t in types]
    
    # Restaurant and food
    if any(t in types_lower for t in ['restaurant', 'food', 'cafe', 'bar', 'bakery', 'pizza', 'takeaway']):
        return "Food & Dining"
    
    # Shopping
    if any(t in types_lower for t in ['store', 'shopping', 'retail', 'clothing', 'jewelry', 'electronics']):
        return "Shopping"
    
    # Entertainment
    if any(t in types_lower for t in ['movie', 'theater', 'cinema', 'entertainment', 'nightclub', 'casino']):
        return "Entertainment"
    
    # Sports and fitness
    if any(t in types_lower for t in ['gym', 'fitness', 'sports', 'stadium', 'swimming', 'tennis']):
        return "Sports & Fitness"
    
    # Healthcare
    if any(t in types_lower for t in ['hospital', 'pharmacy', 'doctor', 'health', 'dentist', 'clinic']):
        return "Healthcare"
    
    # Transport
    if any(t in types_lower for t in ['transit', 'bus', 'train', 'subway', 'taxi', 'car_rental']):
        return "Transport"
    
    # Cultural
    if any(t in types_lower for t in ['museum', 'library', 'art', 'cultural', 'gallery', 'theater']):
        return "Cultural"
    
    # Religious
    if any(t in types_lower for t in ['church', 'mosque', 'temple', 'synagogue', 'place_of_worship']):
        return "Religious"
    
    # Banking and Finance
    if any(t in types_lower for t in ['bank', 'atm', 'finance', 'insurance']):
        return "Banking & Finance"
    
    # Post Office and Services
    if any(t in types_lower for t in ['post_office', 'mail', 'postal']):
        return "Services"
    
    # Childcare and Education
    if any(t in types_lower for t in ['childcare', 'daycare', 'nursery', 'kindergarten']):
        return "Childcare & Education"
    
    # Beauty and Personal Care
    if any(t in types_lower for t in ['beauty_salon', 'hair_care', 'spa', 'nail_salon']):
        return "Beauty & Personal Care"
    
    # Automotive
    if any(t in types_lower for t in ['car_dealer', 'car_repair', 'gas_station', 'parking']):
        return "Automotive"
    
    # Home and Garden
    if any(t in types_lower for t in ['hardware_store', 'garden_center', 'furniture_store']):
        return "Home & Garden"
    
    # Default
    return "Other"


def categorize_places(places):
    """Categorize places of interest into groups."""
    categories = {}
    
    for place in places:
        category = get_place_category(place.get('types', []))
        if category not in categories:
            categories[category] = []
        categories[category].append(place)
    
    # Sort categories by number of places (most first)
    sorted_categories = sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)
    
    return dict(sorted_categories) 