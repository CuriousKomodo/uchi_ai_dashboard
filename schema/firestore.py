from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Content(BaseModel):  # User's preferences
    max_price: int
    num_bedrooms: int
    num_bathrooms: Optional[int] = None
    preferred_location: List[str]  # index
    build_era: List[str]
    property_type: List[str]
    min_energy_rating: str  # EPC?
    exclude_commercial_site: bool
    exclude_high_rise: bool
    has_balcony: bool
    has_garden: bool
    has_private_parking: bool
    refurbishment_needed: List[str]
    open_kitchen: Optional[bool] = None
    hobbies: Optional[str] = None
    has_child: Optional[bool] = None
    has_pet: Optional[bool] = None

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