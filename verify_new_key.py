#!/usr/bin/env python3
"""
Verify New Foursquare API Key

Quick test for the new fsq3 format API key.
"""

import requests

def test_new_api_key(api_key):
    """Test if the new API key works."""
    print("🔑 Testing New API Key")
    print("=" * 25)
    print(f"Key: {api_key[:10]}...{api_key[-4:]}")
    print(f"Length: {len(api_key)}")
    print(f"Starts with fsq3: {'✅' if api_key.startswith('fsq3') else '❌'}")
    print()
    
    if not api_key.startswith('fsq3'):
        print("❌ This is not the correct new API key format!")
        print("You need a key that starts with 'fsq3'")
        return False
    
    # Test the new API
    url = "https://api.foursquare.com/v3/places/search"
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    params = {
        'll': '40.7128,-74.0060',
        'radius': 1000,
        'limit': 1
    }
    
    try:
        print("🌐 Testing API connection...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("🎉 SUCCESS! Your new API key works!")
            data = response.json()
            results = data.get('results', [])
            print(f"Found {len(results)} businesses")
            if results:
                print(f"Sample business: {results[0].get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main verification function."""
    print("🔑 New Foursquare API Key Verifier")
    print("=" * 40)
    print("Enter your new API key (should start with 'fsq3'):")
    
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    if test_new_api_key(api_key):
        print("\n✅ Perfect! Update your .env file with this key:")
        print(f"FOURSQUARE_API_KEY={api_key}")
        print("\nThen run: python main.py")
    else:
        print("\n❌ This key doesn't work. Please:")
        print("1. Make sure you copied the correct 'fsq3' key")
        print("2. Check that your app is approved")
        print("3. Try creating a new app if needed")

if __name__ == "__main__":
    main()
