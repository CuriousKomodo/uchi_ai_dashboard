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
TBC