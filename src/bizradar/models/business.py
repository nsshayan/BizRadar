"""
Business data models for BizRadar application.

Contains data structures for storing and managing business information.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
import json

@dataclass
class Location:
    """Geographic location data."""
    latitude: float
    longitude: float
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Location':
        return cls(**data)

@dataclass
class BusinessHours:
    """Business operating hours."""
    monday: Optional[str] = None
    tuesday: Optional[str] = None
    wednesday: Optional[str] = None
    thursday: Optional[str] = None
    friday: Optional[str] = None
    saturday: Optional[str] = None
    sunday: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BusinessHours':
        return cls(**data)

@dataclass
class Business:
    """Main business data model."""
    fsq_id: str
    name: str
    categories: List[str]
    location: Location
    rating: Optional[float] = None
    hours: Optional[BusinessHours] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    verified: bool = False
    popularity: Optional[float] = None
    first_seen: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    is_competitor: bool = False
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.first_seen is None:
            self.first_seen = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.first_seen:
            data['first_seen'] = self.first_seen.isoformat()
        if self.last_updated:
            data['last_updated'] = self.last_updated.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Business':
        # Convert ISO strings back to datetime objects
        if 'first_seen' in data and data['first_seen']:
            data['first_seen'] = datetime.fromisoformat(data['first_seen'])
        if 'last_updated' in data and data['last_updated']:
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        # Convert location dict to Location object
        if 'location' in data and isinstance(data['location'], dict):
            data['location'] = Location.from_dict(data['location'])
        
        # Convert hours dict to BusinessHours object
        if 'hours' in data and isinstance(data['hours'], dict):
            data['hours'] = BusinessHours.from_dict(data['hours'])
        
        return cls(**data)
    
    def update_from_api_data(self, api_data) -> bool:
        """Update business data from API response. Returns True if changes were made."""
        changes_made = False
        
        # Update basic fields
        if self.name != api_data.name:
            self.name = api_data.name
            changes_made = True
        
        if self.rating != api_data.rating:
            self.rating = api_data.rating
            changes_made = True
        
        if self.popularity != api_data.popularity:
            self.popularity = api_data.popularity
            changes_made = True
        
        if self.verified != api_data.verified:
            self.verified = api_data.verified
            changes_made = True
        
        if self.website != api_data.website:
            self.website = api_data.website
            changes_made = True
        
        if self.phone != api_data.tel:
            self.phone = api_data.tel
            changes_made = True
        
        # Update categories
        if set(self.categories) != set(api_data.categories):
            self.categories = api_data.categories
            changes_made = True
        
        # Update location if changed
        api_location = api_data.location
        if api_location:
            new_location = Location(
                latitude=api_location.get('latitude', self.location.latitude),
                longitude=api_location.get('longitude', self.location.longitude),
                address=api_location.get('address'),
                city=api_location.get('locality'),
                state=api_location.get('region'),
                postal_code=api_location.get('postcode'),
                country=api_location.get('country')
            )
            if new_location != self.location:
                self.location = new_location
                changes_made = True
        
        if changes_made:
            self.last_updated = datetime.now()
        
        return changes_made
    
    def distance_from(self, other_location: Location) -> float:
        """Calculate distance from another location in kilometers."""
        from geopy.distance import geodesic
        return geodesic(
            (self.location.latitude, self.location.longitude),
            (other_location.latitude, other_location.longitude)
        ).kilometers
