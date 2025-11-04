import streamlit as st

def get_criteria_styles():
    """Return the CSS styles for criteria grids."""
    return """
        <style>
        .criteria-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            margin: 15px 0;
        }
        .criteria-item {
            padding: 12px 15px;
            border-radius: 8px;
            font-size: 16px;
            display: flex;
            align-items: center;
        }
        .criteria-item::before {
            content: "✓";
            font-weight: bold;
            margin-right: 10px;
            font-size: 18px;
        }
        .criteria-blue {
            background-color: #e6f3ff;
            border: 1px solid #b3d9ff;
        }
        .criteria-blue::before {
            color: #0066cc;
        }
        .criteria-pink {
            background-color: #ffe6f3;
            border: 1px solid #ffb3d9;
        }
        .criteria-pink::before {
            color: #cc0066;
        }
        .criteria-green {
            background-color: #e6ffe6;
            border: 1px solid #b3ffb3;
        }
        .criteria-green::before {
            color: #006600;
        }
        .criteria-orange {
            background-color: #fff2e6;
            border: 1px solid #ffd9b3;
        }
        .criteria-orange::before {
            color: #cc6600;
        }
        .criteria-purple {
            background-color: #f3e6ff;
            border: 1px solid #d9b3ff;
        }
        .criteria-purple::before {
            color: #6600cc;
        }
        .criteria-teal {
            background-color: #e6fff9;
            border: 1px solid #b3ffd9;
        }
        .criteria-teal::before {
            color: #00cc66;
        }
        </style>
    """

def render_criteria_grid(criterion, title, colors=None):
    """
    Render a criteria grid with the given criteria dictionary.
    
    Args:
        criterion: list of criteria where True values will be displayed
        title: Title for the criteria section
        colors: List of color names to cycle through (defaults to standard colors)
    """
    if colors is None:
        colors = ['blue', 'pink', 'green', 'orange', 'purple', 'teal']
    
    # Add the CSS styles
    st.markdown(get_criteria_styles(), unsafe_allow_html=True)
    
    # Display title
    st.markdown(f"#### {title}")
    
    # Create the criteria grid HTML
    criteria_html = '<div class="criteria-grid">'
    for idx, value in enumerate(criterion):
        color_class = f'criteria-{colors[idx % len(colors)]}'
        formatted_key = value.replace("_", " ").capitalize()
        criteria_html += f'<div class="criteria-item {color_class}">{formatted_key}</div>'
    criteria_html += '</div>'
    
    st.markdown(criteria_html, unsafe_allow_html=True)

def render_property_criteria(property_details):
    """Render matched property criteria."""
    match_criteria = property_details.get("matched_criteria", {})
    
    if match_criteria:
        render_criteria_grid(match_criteria, "Matched Property Criteria")

def render_lifestyle_criteria(property_details):
    """Render matched lifestyle criteria."""
    lifestyle_criteria = property_details.get("matched_lifestyle_criteria", [])
    
    if lifestyle_criteria:
        # Convert list to dictionary format for the grid renderer
        if isinstance(lifestyle_criteria, list):
            lifestyle_dict = {criteria: True for criteria in lifestyle_criteria}
        else:
            # Fallback in case it's still a dictionary
            lifestyle_dict = lifestyle_criteria
        
        # Use different colors for lifestyle criteria to distinguish from property criteria
        lifestyle_colors = ['purple', 'teal', 'orange', 'pink', 'blue', 'green']
        render_criteria_grid(lifestyle_dict, "Matched Lifestyle Criteria", lifestyle_colors) 