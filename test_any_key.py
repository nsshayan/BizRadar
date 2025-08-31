#!/usr/bin/env python3
"""
Test Any Foursquare API Key

Universal tester for any type of Foursquare API key.
"""

import requests

def test_any_api_key(api_key, client_secret=None):
    """Test any API key with multiple methods."""
    print("🔑 Universal Foursquare API Key Tester")
    print("=" * 45)
    print(f"API Key: {api_key}")
    print(f"Key Length: {len(api_key)}")
    print(f"Starts with: {api_key[:4]}")
    print(f"Client Secret: {'Provided' if client_secret else 'Not provided'}")
    print()
    
    test_configs = []
    
    # Test 1: New API (fsq3 keys)
    if api_key.startswith('fsq3'):
        test_configs.extend([
            {
                "name": "New Places API v3",
                "url": "https://api.foursquare.com/v3/places/search",
                "headers": {"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
                "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1}
            },
            {
                "name": "New Places API with version",
                "url": "https://api.foursquare.com/v3/places/search", 
                "headers": {"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
                "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1, "version": "2025-06-17"}
            }
        ])
    
    # Test 2: Legacy API with Client ID + Secret
    if client_secret:
        test_configs.append({
            "name": "Legacy v2 API (Client ID + Secret)",
            "url": "https://api.foursquare.com/v2/venues/search",
            "headers": {"Accept": "application/json"},
            "params": {
                "client_id": api_key,
                "client_secret": client_secret,
                "v": "20230101",
                "ll": "40.7128,-74.0060",
                "radius": 1000,
                "limit": 1
            }
        })
    
    # Test 3: Legacy API userless (Client ID only)
    test_configs.append({
        "name": "Legacy v2 API (Userless)",
        "url": "https://api.foursquare.com/v2/venues/search",
        "headers": {"Accept": "application/json"},
        "params": {
            "client_id": api_key,
            "v": "20230101",
            "ll": "40.7128,-74.0060",
            "radius": 1000,
            "limit": 1,
            "intent": "browse"
        }
    })
    
    # Test 4: OAuth token
    test_configs.append({
        "name": "Legacy v2 API (OAuth Token)",
        "url": "https://api.foursquare.com/v2/venues/search",
        "headers": {"Accept": "application/json"},
        "params": {
            "oauth_token": api_key,
            "v": "20230101",
            "ll": "40.7128,-74.0060",
            "radius": 1000,
            "limit": 1
        }
    })
    
    successful_configs = []
    
    for i, config in enumerate(test_configs, 1):
        print(f"🧪 Test {i}: {config['name']}")
        
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
                
                # Handle different response formats
                if 'results' in data:
                    results = data['results']
                    print(f"   Found {len(results)} results")
                    if results:
                        print(f"   Sample: {results[0].get('name', 'Unknown')}")
                elif 'response' in data and 'venues' in data['response']:
                    venues = data['response']['venues']
                    print(f"   Found {len(venues)} venues")
                    if venues:
                        print(f"   Sample: {venues[0].get('name', 'Unknown')}")
                
                successful_configs.append(config)
                
            else:
                print(f"   ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    return successful_configs

def main():
    """Main test function."""
    print("Enter your API key details:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    client_secret = None
    if not api_key.startswith('fsq3'):
        secret_input = input("Client Secret (optional, press Enter to skip): ").strip()
        if secret_input:
            client_secret = secret_input
    
    successful_configs = test_any_api_key(api_key, client_secret)
    
    if successful_configs:
        print("🎉 WORKING CONFIGURATIONS FOUND!")
        print("=" * 40)
        for i, config in enumerate(successful_configs, 1):
            print(f"{i}. {config['name']}")
            print(f"   URL: {config['url']}")
        
        print("\n✅ Update your .env file with this API key:")
        print(f"FOURSQUARE_API_KEY={api_key}")
        if client_secret:
            print(f"FOURSQUARE_CLIENT_SECRET={client_secret}")
        
        print("\nThen BizRadar can be updated to use the working configuration!")
    else:
        print("❌ NO WORKING CONFIGURATIONS FOUND")
        print("=" * 40)
        print("Next steps:")
        print("1. Check your Foursquare developer account")
        print("2. Verify your app is approved and active")
        print("3. Try creating a new app")
        print("4. Get a new API key (preferably fsq3 format)")

if __name__ == "__main__":
    main()
