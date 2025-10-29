This is a Streamlit dashboard which displays all the recommended properties for a user. 

There should ideally be two versions of the dashboard - one for sales, one for rental. 

**Listing view page requirements**

Sales: 
- Property listing page will contain name card for each property.
- On the name card, the title for each property should contain the address, price, and the number of bedrooms
- The property listing page can be sorted according to user's preference, such as criteria matched or sale price
- choices include: 
                    "Criteria Match: Most to Least",
                    "Price: Low to High",
                     "Price: High to Low",
                     "Bedrooms: Most to Fewest",
                     "Closest to the preferred location",
                     "Newest First"
- User can also filter properties to view properties within 2km of their preferred neighborhood
- User can also filter properties for fields inside "description_analysis", such as "is_chain_free" = True, 
- "years_left_on_lease" > <USER_LEASE_YEAR_THRESHOLD> and "service_charge" < <USER_SERVICE_CHARGE_THRESHOLD>,  or "journey".get("total") < <USER_MAX_JOURNEY_MINUTES>. 


Rental:
- Property listing page will contain name card for each property.  
- The property listing page can be sorted according to user's preference, such as criteria matched or monthly rent
- On the name card, the title for each property should contain the address, monthly rent and the number of bedrooms
- Furnishing type should be displayed on the name card. 
- Date of availability should be displayed on the name card as well. We need a function to convert "let_available" from timestamp to date
- The property listing page can be sorted according to user's preference, such as criteria matched or sale price
- choices include: 
                    "Criteria Match: Most to Least",
                    "Rent: Low to High",
                     "Bedrooms: Most to Fewest",
                     "Closest to the preferred location",
                     "Newest First"
- User can also filter properties to view properties within 2km of their preferred neighborhood
- User can filter properties based on furnishing type, and deposit < <USER_DEPOSIT_THRESHOLD>, or "journey".get("total") < <USER_MAX_JOURNEY_MINUTES>.


**Property view page requirements**

Sales (property tab)
- The title of the property is address of the property. 
- The subtitle is "<PRICE> | <NUM_BEDROOMS>"
- Photo gallery (existing version, no need to modify)
- AI summary section
- Matched criteria
- Property details section: prioritise years_left_on_lease, is_chain_free and service_charge


Rental (property tab)
- The title of the property is address of the property. 
- The subtitle is "<MONTHLY_RENT> | <NUM_BEDROOMS>, <FURNISHING_TYPE>"
- Photo gallery (existing version, no need to modify)
- AI summary section
- Matched criteria
- Property details section: prioritise let_available, deposit and minimum_tenancy_months

A small UI addition to both Sales and Rental property tab: 
Install a bar chart to compare the property price with the average price for the same number of bedrooms (sales), 
or compare the rent price with the average price for the smae number of bedrooms (rental)
Place it next to the property details section. Display "data not available" if the average price/rent is not found


Sales & Rental (location tab)
- Keep things as they are, except we want to include some commute journey information next to the map view, underneath the nearest stations
- Commute journey section: display the workplace location (from user submission content), and the "total" time taken, as well as journey details i.e. walk for X min -> bus N for Y min. Use emoji for each transport mode
- an example field of property_journey["journey"]:
- {"total": 18, "modes": {"walk": {"duration" : 12},"bus": {"duration": 6, "legs": [{"route": 26, "from": "Liverpool Street Station", "to": "Shoreditch Church"}]}}}

- A UI change to the demographics section: the demographics metric such as crime rates, education rate are not properly color coded - please fix them
