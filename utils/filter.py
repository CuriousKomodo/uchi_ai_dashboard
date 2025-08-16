def criteria_match_count(prop):
    """Count the number of matched criteria for a property."""
    match_criteria = prop.get("match_output", {})
    match_criteria_additional = prop.get("matched_criteria", {})
    
    # Count boolean matches from match_output
    count = sum(1 for k, v in match_criteria.items() if isinstance(v, bool) and v)
    
    # Add count from matched_criteria (these are already matched)
    count += len(match_criteria_additional)
    
    return count


def sort_by_chosen_option(sort_by, shortlist):
    if sort_by == "Price: Low to High":
        shortlist.sort(key=lambda x: x.get("price", 0))
    elif sort_by == "Price: High to Low":
        shortlist.sort(key=lambda x: x.get("price", 0), reverse=True)
    elif sort_by == "Bedrooms: Most to Fewest":
        shortlist.sort(key=lambda x: x.get("num_bedrooms", 0), reverse=True)
    elif sort_by == "Commute time to work: Shortest to Longest":
        shortlist.sort(key=lambda x: x.get('journey', {"duration": 500}).get('duration'))
    elif sort_by == "Criteria Match: Most to Least":
        shortlist.sort(key=criteria_match_count, reverse=True)
    elif sort_by == "Closest to the preferred location":
        shortlist.sort(key=lambda x: x.get("distance_to_preferred_location", 500))
    elif sort_by == "Newest First":
        shortlist.sort(key=lambda x: x.get("created_at", ""), reverse=True)


if __name__ == "__main__":
    shortlist = []

