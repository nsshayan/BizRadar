#!/usr/bin/env python3
"""
Test Current Foursquare API Configuration

Test the current BizRadar API client with your API key.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_current_api():
    """Test the current API configuration."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🔍 Testing Current BizRadar API Configuration")
    print("=" * 50)
    print(f"API Key: {api_key}")
    print(f"Key Length: {len(api_key)}")
    print(f"Key Type: {'Legacy Client ID' if len(api_key) == 48 and not api_key.startswith('fsq3') else 'Modern API Key' if api_key.startswith('fsq3') else 'Unknown'}")
    print()
    
    try:
        from bizradar.api.foursquare_client import FoursquareClient
        
        print("🚀 Creating Foursquare Client")
        client = FoursquareClient(api_key)
        print(f"✅ Client created successfully")
        print(f"Base URL: {client.BASE_URL}")
        print()
        
        print("🔍 Testing Search Nearby")
        # Test search in NYC
        places = client.search_nearby(40.7128, -74.0060, 1000, limit=3)
        
        if places:
            print(f"✅ SUCCESS! Found {len(places)} places")
            print()
            print("📍 Sample Results:")
            for i, place in enumerate(places, 1):
                print(f"{i}. {place.name}")
                print(f"   Categories: {', '.join(place.categories)}")
                print(f"   Rating: {place.rating if place.rating else 'No rating'}")
                print(f"   Verified: {'Yes' if place.verified else 'No'}")
                print(f"   Location: {place.location.get('address', 'No address')}")
                print()
            
            return True
        else:
            print("❌ No places returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_place_details():
    """Test getting place details."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    try:
        from bizradar.api.foursquare_client import FoursquareClient
        
        client = FoursquareClient(api_key)
        
        print("🔍 Testing Place Details")
        # First get a place from search
        places = client.search_nearby(40.7128, -74.0060, 1000, limit=1)
        
        if places:
            place = places[0]
            print(f"Getting details for: {place.name}")
            
            details = client.get_place_details(place.fsq_id)
            if details:
                print("✅ Place details retrieved successfully")
                print(f"Name: {details.name}")
                print(f"Categories: {', '.join(details.categories)}")
                return True
            else:
                print("❌ Failed to get place details")
                return False
        else:
            print("❌ No places found for details test")
            return False
            
    except Exception as e:
        print(f"❌ Error in place details test: {e}")
        return False

def test_trending_places():
    """Test getting trending places."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    try:
        from bizradar.api.foursquare_client import FoursquareClient
        
        client = FoursquareClient(api_key)
        
        print("🔍 Testing Trending Places")
        trending = client.get_trending_places(40.7128, -74.0060, 1000)
        
        if trending:
            print(f"✅ Found {len(trending)} trending places")
            for place in trending[:2]:  # Show first 2
                print(f"- {place.name} (popularity: {place.popularity})")
            return True
        else:
            print("❌ No trending places found")
            return False
            
    except Exception as e:
        print(f"❌ Error in trending test: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 BizRadar API Integration Test")
    print("=" * 50)
    
    # Test basic search
    search_success = test_current_api()
    
    if search_success:
        print("\n" + "="*50)
        
        # Test additional features
        details_success = test_place_details()
        trending_success = test_trending_places()
        
        print("\n" + "="*50)
        print("📊 Test Results Summary")
        print("="*25)
        print(f"✅ Basic Search: {'PASS' if search_success else 'FAIL'}")
        print(f"✅ Place Details: {'PASS' if details_success else 'FAIL'}")
        print(f"✅ Trending Places: {'PASS' if trending_success else 'FAIL'}")
        
        if search_success and details_success:
            print("\n🎉 SUCCESS! Your API key is working correctly!")
            print("🚀 You can now run the full BizRadar application:")
            print("   python main.py")
        else:
            print("\n⚠️  Some features may not work correctly")
            print("But basic functionality should work for BizRadar")
    else:
        print("\n❌ API key is not working correctly")
        print("Please check:")
        print("1. API key is correct in .env file")
        print("2. API key has proper permissions")
        print("3. Foursquare account is active")

if __name__ == "__main__":
    main()
