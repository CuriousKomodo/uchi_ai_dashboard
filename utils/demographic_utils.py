def snake_case_to_title(snake_str):
    """Convert snake_case string to Title Case."""
    return ' '.join(word.capitalize() for word in snake_str.split('_'))


def format_description_analysis_value(value):
    """Format values from description_analysis for display."""
    if value is None:
        return "Ask Agent"
    elif isinstance(value, bool):
        return "Yes" if value else "No"
    elif isinstance(value, list):
        if not value:
            return "Ask Agent"
        return ", ".join(str(item) for item in value)
    else:
        return str(value)


def get_population_growth_color(growth_str):
    """Determine color for population growth based on positive/negative value."""
    if not growth_str:
        return "normal"
    
    # Extract numeric value from string like "5%" or "-2%"
    try:
        numeric_value = float(growth_str.replace('%', '').replace(',', ''))
        return "normal" if numeric_value > 0 else "inverse"
    except (ValueError, AttributeError):
        return "normal"


def get_deprivation_rate_color(rate_str):
    """Determine color for deprivation rate: <20% green, >40% red, else normal."""
    if not rate_str:
        return "normal"
    
    try:
        numeric_value = float(rate_str.replace('%', '').replace(',', ''))
        if numeric_value < 20:
            return "normal"
        elif numeric_value > 40:
            return "inverse"
        else:
            return "off"
    except (ValueError, AttributeError):
        return "normal"


def get_crime_rate_color(rate_str):
    """Determine color for crime rate: <50 green, >104 red, else normal."""
    if not rate_str:
        return "normal"
    
    try:
        numeric_value = float(rate_str.replace('%', '').replace(',', ''))
        if numeric_value < 50:
            return "normal"
        elif numeric_value > 104:
            return "inverse"
        else:
            return "off"
    except (ValueError, AttributeError):
        return "normal" 