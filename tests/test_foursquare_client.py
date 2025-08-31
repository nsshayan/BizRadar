"""
Unit tests for Foursquare API client.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bizradar.api.foursquare_client import FoursquareClient, PlaceData, RateLimiter

class TestRateLimiter(unittest.TestCase):
    """Test cases for RateLimiter class."""
    
    def setUp(self):
        self.rate_limiter = RateLimiter(max_requests=5, time_window=60)
    
    def test_initial_state(self):
        """Test initial state allows requests."""
        self.assertTrue(self.rate_limiter.can_make_request())
    
    def test_rate_limiting(self):
        """Test rate limiting functionality."""
        # Make maximum allowed requests
        for _ in range(5):
            self.assertTrue(self.rate_limiter.can_make_request())
            self.rate_limiter.record_request()
        
        # Next request should be blocked
        self.assertFalse(self.rate_limiter.can_make_request())
    
    @patch('time.time')
    def test_time_window_reset(self, mock_time):
        """Test that rate limit resets after time window."""
        # Start at time 0
        mock_time.return_value = 0
        
        # Make maximum requests
        for _ in range(5):
            self.rate_limiter.record_request()
        
        # Should be blocked
        self.assertFalse(self.rate_limiter.can_make_request())
        
        # Move time forward beyond window
        mock_time.return_value = 70
        
        # Should be allowed again
        self.assertTrue(self.rate_limiter.can_make_request())

class TestFoursquareClient(unittest.TestCase):
    """Test cases for FoursquareClient class."""
    
    def setUp(self):
        self.api_key = "test_api_key"
        self.client = FoursquareClient(self.api_key)
    
    def test_initialization(self):
        """Test client initialization."""
        self.assertEqual(self.client.api_key, self.api_key)
        self.assertIsNotNone(self.client.rate_limiter)
        self.assertIsNotNone(self.client.session)
        self.assertEqual(
            self.client.session.headers['Authorization'], 
            f'Bearer {self.api_key}'
        )
    
    @patch('requests.Session.get')
    def test_successful_request(self, mock_get):
        """Test successful API request."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        result = self.client._make_request("search", {"test": "param"})
        
        self.assertIsNotNone(result)
        self.assertEqual(result, {"results": []})
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_rate_limited_request(self, mock_get):
        """Test handling of rate limited response."""
        # Mock rate limited response, then successful response
        rate_limited_response = Mock()
        rate_limited_response.status_code = 429
        
        successful_response = Mock()
        successful_response.status_code = 200
        successful_response.json.return_value = {"results": []}
        
        mock_get.side_effect = [rate_limited_response, successful_response]
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            result = self.client._make_request("search")
        
        self.assertIsNotNone(result)
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('requests.Session.get')
    def test_failed_request(self, mock_get):
        """Test handling of failed request."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_get.return_value = mock_response
        
        result = self.client._make_request("search")
        
        self.assertIsNone(result)
    
    @patch.object(FoursquareClient, '_make_request')
    def test_search_nearby(self, mock_request):
        """Test search_nearby method."""
        # Mock API response
        mock_response = {
            "results": [
                {
                    "fsq_id": "test_id_1",
                    "name": "Test Business",
                    "categories": [{"name": "Restaurant"}],
                    "location": {"latitude": 40.7128, "longitude": -74.0060},
                    "rating": 4.5,
                    "verified": True
                }
            ]
        }
        mock_request.return_value = mock_response
        
        places = self.client.search_nearby(40.7128, -74.0060, 1000)
        
        self.assertEqual(len(places), 1)
        self.assertIsInstance(places[0], PlaceData)
        self.assertEqual(places[0].fsq_id, "test_id_1")
        self.assertEqual(places[0].name, "Test Business")
        self.assertEqual(places[0].rating, 4.5)
    
    @patch.object(FoursquareClient, '_make_request')
    def test_search_nearby_with_categories(self, mock_request):
        """Test search_nearby with category filter."""
        mock_request.return_value = {"results": []}
        
        self.client.search_nearby(
            40.7128, -74.0060, 1000, 
            categories=["Restaurant", "Coffee Shop"]
        )
        
        # Verify the request was made with categories parameter
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertIn("categories", kwargs.get("params", {}))
    
    @patch.object(FoursquareClient, '_make_request')
    def test_get_place_details(self, mock_request):
        """Test get_place_details method."""
        mock_response = {
            "fsq_id": "test_id",
            "name": "Test Business",
            "categories": [{"name": "Restaurant"}],
            "location": {"latitude": 40.7128, "longitude": -74.0060},
            "rating": 4.5
        }
        mock_request.return_value = mock_response
        
        place = self.client.get_place_details("test_id")
        
        self.assertIsNotNone(place)
        self.assertIsInstance(place, PlaceData)
        self.assertEqual(place.fsq_id, "test_id")
    
    @patch.object(FoursquareClient, '_make_request')
    def test_get_place_details_not_found(self, mock_request):
        """Test get_place_details with non-existent place."""
        mock_request.return_value = None
        
        place = self.client.get_place_details("non_existent_id")
        
        self.assertIsNone(place)
    
    @patch.object(FoursquareClient, 'search_nearby')
    def test_get_trending_places(self, mock_search):
        """Test get_trending_places method."""
        # Mock places with different popularity scores
        mock_places = [
            PlaceData("id1", "Business 1", ["Restaurant"], {}, popularity=0.8),
            PlaceData("id2", "Business 2", ["Cafe"], {}, popularity=0.6),
            PlaceData("id3", "Business 3", ["Shop"], {}, popularity=0.9),
            PlaceData("id4", "Business 4", ["Bar"], {}, popularity=0.5),
        ]
        mock_search.return_value = mock_places
        
        trending = self.client.get_trending_places(40.7128, -74.0060)
        
        # Should return places with popularity > 0.7, sorted by popularity
        self.assertEqual(len(trending), 2)
        self.assertEqual(trending[0].fsq_id, "id3")  # Highest popularity first
        self.assertEqual(trending[1].fsq_id, "id1")

class TestPlaceData(unittest.TestCase):
    """Test cases for PlaceData class."""
    
    def test_place_data_creation(self):
        """Test PlaceData object creation."""
        place = PlaceData(
            fsq_id="test_id",
            name="Test Place",
            categories=["Restaurant", "Italian"],
            location={"latitude": 40.7128, "longitude": -74.0060},
            rating=4.5,
            verified=True
        )
        
        self.assertEqual(place.fsq_id, "test_id")
        self.assertEqual(place.name, "Test Place")
        self.assertEqual(len(place.categories), 2)
        self.assertEqual(place.rating, 4.5)
        self.assertTrue(place.verified)

if __name__ == '__main__':
    unittest.main()
