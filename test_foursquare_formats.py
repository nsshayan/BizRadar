#!/usr/bin/env python3
"""
Test different Foursquare API formats and authentication methods.
"""

import os
import requests
from dotenv import load_dotenv

def test_multiple_api_formats():
    """Test different API formats and authentication methods."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🔍 Testing Multiple Foursquare API Formats")
    print("=" * 50)
    print(f"API Key: {api_key}")
    print(f"Key starts with: {api_key[:4] if api_key else 'None'}")
    print()
    
    # Test configurations
    test_configs = [
        {
            "name": "New Places API v1",
            "url": "https://places-api.foursquare.com/places/search",
            "headers": {"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1, "version": "v1"}
        },
        {
            "name": "New Places API (no version)",
            "url": "https://places-api.foursquare.com/places/search",
            "headers": {"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1}
        },
        {
            "name": "Legacy API v3",
            "url": "https://api.foursquare.com/v3/places/search",
            "headers": {"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1}
        },
        {
            "name": "Legacy API v2 (OAuth)",
            "url": "https://api.foursquare.com/v2/venues/search",
            "headers": {"Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1, "oauth_token": api_key, "v": "20230101"}
        },
        {
            "name": "Legacy API v2 (Client Credentials)",
            "url": "https://api.foursquare.com/v2/venues/search",
            "headers": {"Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1, "client_id": api_key, "client_secret": "dummy", "v": "20230101"}
        }
    ]
    
    successful_config = None
    
    for i, config in enumerate(test_configs, 1):
        print(f"🧪 Test {i}: {config['name']}")
        print(f"   URL: {config['url']}")
        print(f"   Headers: {config['headers']}")
        print(f"   Params: {config['params']}")
        
        try:
            response = requests.get(
                config['url'], 
                headers=config['headers'], 
                params=config['params'], 
                timeout=10
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                data = response.json()
                if 'response' in data and 'venues' in data['response']:
                    # v2 API format
                    venues = data['response']['venues']
                    print(f"   Found {len(venues)} venues")
                    if venues:
                        print(f"   Sample: {venues[0].get('name', 'Unknown')}")
                elif 'results' in data:
                    # v3 API format
                    results = data['results']
                    print(f"   Found {len(results)} results")
                    if results:
                        print(f"   Sample: {results[0].get('name', 'Unknown')}")
                successful_config = config
                break
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    if successful_config:
        print("🎉 FOUND WORKING CONFIGURATION!")
        print("=" * 40)
        print(f"Working format: {successful_config['name']}")
        print(f"URL: {successful_config['url']}")
        print("This configuration will be used to update BizRadar.")
        return successful_config
    else:
        print("❌ NO WORKING CONFIGURATION FOUND")
        print("=" * 40)
        print("Possible issues:")
        print("1. API key is invalid or expired")
        print("2. API key doesn't have required permissions")
        print("3. Account needs verification")
        print("4. Using wrong type of credentials")
        return None

def analyze_api_key():
    """Analyze the API key format to determine its type."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("\n🔍 API Key Analysis")
    print("=" * 25)
    
    if not api_key:
        print("❌ No API key found")
        return
    
    print(f"Length: {len(api_key)}")
    print(f"Starts with: {api_key[:10]}")
    print(f"Ends with: {api_key[-10:]}")
    
    if api_key.startswith('fsq3'):
        print("✅ Format: New Foursquare API key (v3+)")
    elif len(api_key) == 48 and api_key.isupper():
        print("✅ Format: Legacy Foursquare Client ID")
    elif len(api_key) == 48:
        print("⚠️  Format: Possible legacy OAuth token")
    else:
        print("❓ Format: Unknown - may need verification")

def main():
    """Main test function."""
    analyze_api_key()
    successful_config = test_multiple_api_formats()
    
    if successful_config:
        print("\n🛠️  Next Steps:")
        print("1. BizRadar will be updated to use the working configuration")
        print("2. You can then run: python main.py")
        print("3. All features should work correctly")
    else:
        print("\n🛠️  Troubleshooting Steps:")
        print("1. Verify your API key in the Foursquare Developer Portal")
        print("2. Check if your app is approved and active")
        print("3. Try regenerating the API key")
        print("4. Consider creating a new app")

if __name__ == "__main__":
    main()
