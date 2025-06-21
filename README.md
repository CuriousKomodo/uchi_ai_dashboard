# UchiAI Dashboard

A comprehensive property search and analysis dashboard powered by AI.

## Features

### 🗺️ Enhanced Map View with Places of Interest

The property location view now displays a comprehensive map showing various places of interest within 1km of the property:

#### Map Markers Include:
- **🏠 Property** - Red home icon (the property itself)
- **🏫 Schools** - Blue graduation cap (nearby educational institutions)
- **🛒 Supermarkets** - Green shopping cart (grocery stores)
- **🌳 Green Spaces** - Dark green tree (parks and recreational areas)
- **🍽️ Restaurants** - Orange utensils (dining establishments)
- **🛍️ Shopping** - Purple shopping bag (retail stores)
- **🎬 Entertainment** - Dark red film (cinemas, theaters)
- **💪 Sports/Gym** - Dark blue dumbbell (fitness facilities)
- **🏥 Healthcare** - Red medkit (hospitals, clinics, pharmacies)
- **🚌 Transport** - Dark green bus (transportation hubs)
- **🏛️ Cultural** - Cadet blue landmark (museums, libraries)
- **🙏 Religious** - Brown pray icon (places of worship)
- **🏦 Banking** - Dark green university icon (banks, ATMs)
- **📮 Post Office** - Navy envelope (postal services)
- **👶 Childcare** - Pink baby (daycare, nurseries)

#### Features:
- **Interactive Popups**: Click any marker to see detailed information including ratings, addresses, and links to Google Maps
- **Smart Categorization**: Places are automatically categorized and color-coded based on their type
- **Comprehensive Legend**: Clear legend explaining all marker types
- **Summary Statistics**: Shows count of different place types found nearby
- **Enhanced Display**: Places of interest are also displayed in an organized grid layout below the map

#### Technical Implementation:
- Uses Folium for interactive map rendering
- Automatic coordinate extraction from Google Maps place URIs
- Fallback geocoding for addresses without coordinates
- Responsive design with proper error handling
- Integration with existing property data structure

This enhancement provides property buyers with a comprehensive view of the neighborhood amenities, helping them make informed decisions about their potential new home.