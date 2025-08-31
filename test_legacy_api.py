#!/usr/bin/env python3
"""
Test Legacy Foursquare API v2 with Client ID.

Since your API key appears to be a legacy Client ID, let's test the v2 API.
"""

import os
import requests
from dotenv import load_dotenv

def test_legacy_v2_api():
    """Test the legacy v2 API with Client ID."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🔍 Testing Legacy Foursquare API v2")
    print("=" * 40)
    print(f"Client ID: {api_key}")
    print()
    
    # For v2 API, we need both client_id and client_secret
    # But let's try with just client_id first
    
    url = "https://api.foursquare.com/v2/venues/search"
    params = {
        "client_id": api_key,
        "client_secret": "dummy_secret",  # This might not work without real secret
        "v": "20230101",  # Version date format for v2 API
        "ll": "40.7128,-74.0060",
        "radius": 1000,
        "limit": 5
    }
    
    print("🧪 Test 1: v2 API with Client ID + dummy secret")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            if 'response' in data and 'venues' in data['response']:
                venues = data['response']['venues']
                print(f"Found {len(venues)} venues")
                for venue in venues[:3]:
                    print(f"- {venue.get('name', 'Unknown')}")
                return True
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print()
    
    # Try with OAuth token approach
    print("🧪 Test 2: v2 API with OAuth token")
    params_oauth = {
        "oauth_token": api_key,
        "v": "20230101",
        "ll": "40.7128,-74.0060",
        "radius": 1000,
        "limit": 5
    }
    
    try:
        response = requests.get(url, params=params_oauth, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            data = response.json()
            if 'response' in data and 'venues' in data['response']:
                venues = data['response']['venues']
                print(f"Found {len(venues)} venues")
                for venue in venues[:3]:
                    print(f"- {venue.get('name', 'Unknown')}")
                return True
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def test_userless_access():
    """Test userless access with Client ID only."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("\n🔍 Testing Userless Access (Client ID only)")
    print("=" * 45)
    
    # Some endpoints might work with just client_id for userless access
    url = "https://api.foursquare.com/v2/venues/search"
    params = {
        "client_id": api_key,
        "v": "20230101",
        "ll": "40.7128,-74.0060",
        "radius": 1000,
        "limit": 5,
        "intent": "browse"  # Userless intent
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Userless access works!")
            data = response.json()
            if 'response' in data and 'venues' in data['response']:
                venues = data['response']['venues']
                print(f"Found {len(venues)} venues")
                for venue in venues[:3]:
                    print(f"- {venue.get('name', 'Unknown')}")
                    print(f"  Categories: {[cat['name'] for cat in venue.get('categories', [])]}")
                return True
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def check_api_key_status():
    """Check if the API key is valid by testing a simple endpoint."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("\n🔍 Checking API Key Status")
    print("=" * 30)
    
    # Try to get venue categories (usually works with just client_id)
    url = "https://api.foursquare.com/v2/venues/categories"
    params = {
        "client_id": api_key,
        "v": "20230101"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API key is valid!")
            data = response.json()
            if 'response' in data and 'categories' in data['response']:
                categories = data['response']['categories']
                print(f"Found {len(categories)} venue categories")
                return True
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    return False

def main():
    """Main test function."""
    print("🚀 Legacy Foursquare API v2 Tester")
    print("=" * 40)
    
    # Check if API key is valid
    key_valid = check_api_key_status()
    
    if key_valid:
        print("\n✅ API key is valid, testing venue search...")
        
        # Test userless access first (most likely to work)
        userless_success = test_userless_access()
        
        if userless_success:
            print("\n🎉 SUCCESS! Legacy v2 API works with userless access!")
            print("BizRadar can be updated to use the v2 API.")
        else:
            # Try other methods
            legacy_success = test_legacy_v2_api()
            
            if legacy_success:
                print("\n🎉 SUCCESS! Legacy v2 API works!")
            else:
                print("\n❌ Legacy v2 API not working")
    else:
        print("\n❌ API key appears to be invalid or expired")
        print("Please check your Foursquare developer account")

if __name__ == "__main__":
    main()
