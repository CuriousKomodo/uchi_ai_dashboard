# def criteria_match_count(prop):
#     return sum(1 for k, v in prop.get("match_output", {}).items() if isinstance(v, bool) and v)


def sort_by_chosen_option(sort_by, shortlist):
    if sort_by == "Price: Low to High":
        shortlist.sort(key=lambda x: x.get("price", 0))
    elif sort_by == "Bedrooms: Most to Fewest":
        shortlist.sort(key=lambda x: x.get("num_bedrooms", 0), reverse=True)
    elif sort_by == "Commute time to work: Shortest to Longest":
        shortlist.sort(key=lambda x: x.get('journey', {"duration": 500}).get('duration'), reverse=True)
    # elif sort_by == "Criteria Match: Most to Least":
    #     shortlist.sort(key=criteria_match_count, reverse=True)


if __name__ == "__main__":
    shortlist = []

