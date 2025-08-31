"""
Foursquare Places API Client

Handles all interactions with the Foursquare Places API including
authentication, rate limiting, and error handling.
"""

import time
import requests
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PlaceData:
    """Data structure for place information from Foursquare API."""
    fsq_id: str
    name: str
    categories: List[str]
    location: Dict[str, any]
    rating: Optional[float] = None
    hours: Optional[Dict] = None
    website: Optional[str] = None
    tel: Optional[str] = None
    verified: bool = False
    popularity: Optional[float] = None

class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, max_requests: int = 50, time_window: int = 3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def can_make_request(self) -> bool:
        """Check if we can make a request without exceeding rate limits."""
        now = time.time()
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        return len(self.requests) < self.max_requests
    
    def record_request(self):
        """Record that a request was made."""
        self.requests.append(time.time())

class FoursquareClient:
    """Client for interacting with Foursquare Places API."""
    
    BASE_URL = "https://api.foursquare.com/v3/places"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.rate_limiter = RateLimiter()
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to the Foursquare API with rate limiting and error handling."""
        if not self.rate_limiter.can_make_request():
            logger.warning("Rate limit reached, waiting...")
            time.sleep(60)  # Wait 1 minute before retrying
        
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            response = self.session.get(url, params=params, timeout=30)
            self.rate_limiter.record_request()
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                logger.warning("Rate limited by API, waiting...")
                time.sleep(60)
                return self._make_request(endpoint, params)  # Retry
            else:
                logger.error(f"API request failed: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception: {e}")
            return None
    
    def search_nearby(self, latitude: float, longitude: float, radius: int = 1000, 
                     categories: Optional[List[str]] = None, limit: int = 50) -> List[PlaceData]:
        """Search for places near a given location."""
        params = {
            'll': f"{latitude},{longitude}",
            'radius': radius,
            'limit': min(limit, 50),  # API limit
            'fields': 'fsq_id,name,categories,location,rating,hours,website,tel,verified,popularity'
        }
        
        if categories:
            params['categories'] = ','.join(categories)
        
        response = self._make_request('search', params)
        if not response:
            return []
        
        places = []
        for result in response.get('results', []):
            try:
                place = PlaceData(
                    fsq_id=result['fsq_id'],
                    name=result['name'],
                    categories=[cat['name'] for cat in result.get('categories', [])],
                    location=result.get('location', {}),
                    rating=result.get('rating'),
                    hours=result.get('hours'),
                    website=result.get('website'),
                    tel=result.get('tel'),
                    verified=result.get('verified', False),
                    popularity=result.get('popularity')
                )
                places.append(place)
            except KeyError as e:
                logger.warning(f"Missing required field in API response: {e}")
                continue
        
        return places
    
    def get_place_details(self, fsq_id: str) -> Optional[PlaceData]:
        """Get detailed information about a specific place."""
        params = {
            'fields': 'fsq_id,name,categories,location,rating,hours,website,tel,verified,popularity,description,photos'
        }
        
        response = self._make_request(f'{fsq_id}', params)
        if not response:
            return None
        
        try:
            result = response
            return PlaceData(
                fsq_id=result['fsq_id'],
                name=result['name'],
                categories=[cat['name'] for cat in result.get('categories', [])],
                location=result.get('location', {}),
                rating=result.get('rating'),
                hours=result.get('hours'),
                website=result.get('website'),
                tel=result.get('tel'),
                verified=result.get('verified', False),
                popularity=result.get('popularity')
            )
        except KeyError as e:
            logger.error(f"Missing required field in place details: {e}")
            return None
    
    def get_trending_places(self, latitude: float, longitude: float, radius: int = 1000) -> List[PlaceData]:
        """Get trending places in the area (places with recent activity)."""
        # Note: This is a simplified implementation. In a real scenario, you might use
        # additional API endpoints or analyze popularity trends over time
        places = self.search_nearby(latitude, longitude, radius)
        
        # Filter for places with high popularity or recent verification
        trending = [place for place in places if place.popularity and place.popularity > 0.7]
        return sorted(trending, key=lambda x: x.popularity or 0, reverse=True)[:10]
