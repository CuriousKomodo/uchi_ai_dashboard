from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel


class Content(BaseModel):
    listing_type: Optional[str] = None  # User's preferences
    max_price: Optional[int] = None
    max_monthly_rent: Optional[int] = None
    num_bedrooms: int
    num_bathrooms: Optional[int] = None
    property_type: List[str]
    user_preference_tags: List[str] = None
    user_preference: Optional[str] = None
    hobbies: Optional[str] = None
    has_child: Optional[bool] = None
    has_pet: Optional[bool] = None
    workplace_location: Optional[str] = None
    preferred_location: Optional[str] = None
    min_lease_year: Optional[int] = None
    buying_alone: Optional[bool] = None
    timeline: Optional[str] = None  # Sales
    motivation: Optional[str] = None
    school_types: Optional[List[str]] = []

    # Rental
    furnishing_preference: Optional[Union[str, List[str]]] = None
    deposit: Optional[int] = None
    let_available: Optional[datetime] = None


# todo: worth adding a new class for Rental vs. Sale

class Submission(BaseModel):
    id: Optional[str]
    user_id: str
    email: str
    content: Content
    is_active: Optional[bool] = None

class Property(BaseModel):
    id: str
    address: str
    postcode: str  # index TODO in the future
    deprivation_level: float
    num_bedrooms: int  # index
    num_bathrooms: Optional[int] = None  # index
    price: float  # index
    has_garden: Optional[bool] = None
    has_balcony: Optional[bool] = None
    key_features: List[str]
    created_at: datetime

class Extraction(BaseModel):
    id: Optional[str]
    property_id: str

class PlaceofInterest(BaseModel):
    displayName: str
    rating: str
    types: Optional[List[str]]

class ShortListItem(BaseModel):
    pass