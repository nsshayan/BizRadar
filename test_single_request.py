#!/usr/bin/env python3
"""
Test a single API request to verify it's working.
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_single_request():
    """Test a single API request."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🔍 Testing Single API Request")
    print("=" * 35)
    print(f"API Key: {api_key}")
    print()
    
    try:
        from bizradar.api.foursquare_client import FoursquareClient
        
        print("🚀 Creating Foursquare Client")
        client = FoursquareClient(api_key)
        print(f"✅ Client created successfully")
        print(f"Base URL: {client.BASE_URL}")
        print(f"API Version: {client.API_VERSION}")
        print()
        
        print("🔍 Testing Single Search Request")
        print("Searching for places near NYC...")
        
        # Wait a bit to avoid rate limits
        time.sleep(2)
        
        places = client.search_nearby(40.7128, -74.0060, 1000, limit=1)
        
        if places:
            print(f"✅ SUCCESS! Found {len(places)} place(s)")
            print()
            print("📍 Result:")
            place = places[0]
            print(f"Name: {place.name}")
            print(f"Categories: {', '.join(place.categories)}")
            print(f"Rating: {place.rating if place.rating else 'No rating'}")
            print(f"Verified: {'Yes' if place.verified else 'No'}")
            print(f"Address: {place.location.get('address', 'No address')}")
            print(f"FSQ ID: {place.fsq_id}")
            
            return True
        else:
            print("❌ No places returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 Single Request API Test")
    print("=" * 30)
    
    success = test_single_request()
    
    if success:
        print("\n🎉 SUCCESS! Your API is working correctly!")
        print("=" * 45)
        print("✅ API Key: Working")
        print("✅ Authentication: Working") 
        print("✅ API Version Header: Working")
        print("✅ Places API: Working")
        print()
        print("🚀 You can now run the full BizRadar application:")
        print("   python main.py")
        print()
        print("💡 Note: If you see rate limit messages, just wait a moment")
        print("   and the app will continue working.")
    else:
        print("\n❌ API test failed")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
