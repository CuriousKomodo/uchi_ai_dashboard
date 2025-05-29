def extract_conclusion(text):
    """Extract and clean content after 'Conclusion' from a paragraph."""
    if not text or not isinstance(text, str):
        return ""
    
    # Find the position of "Conclusion" (case-insensitive)
    conclusion_pos = text.lower().find("conclusion")
    
    if conclusion_pos == -1:
        return ""  # No conclusion found
    
    # Extract everything after "Conclusion"
    conclusion_text = text[conclusion_pos + len("conclusion"):].strip()
    
    # Clean the text
    # Remove leading punctuation and whitespace
    conclusion_text = conclusion_text.lstrip(":.,;- \t\n\r")
    
    # Remove extra whitespace and normalize spacing
    conclusion_text = " ".join(conclusion_text.split())
    
    return conclusion_text 