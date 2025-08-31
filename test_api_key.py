#!/usr/bin/env python3
"""
Test Foursquare API Key

This script tests your Foursquare API key and helps diagnose authentication issues.
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_api_key_format(api_key):
    """Test if API key has the correct format."""
    print("🔍 Testing API Key Format")
    print("-" * 30)
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"✓ API key length: {len(api_key)} characters")
    print(f"✓ API key preview: {api_key[:10]}...{api_key[-4:]}")
    
    # Check format
    if len(api_key) < 20:
        print("⚠️  API key seems too short")
        return False
    
    if not api_key.replace('-', '').replace('_', '').isalnum():
        print("⚠️  API key contains unexpected characters")
        return False
    
    print("✅ API key format looks correct")
    return True

def test_api_connection(api_key):
    """Test API connection with different endpoints."""
    print("\n🌐 Testing API Connection")
    print("-" * 30)
    
    # Test 1: Simple search endpoint
    print("Test 1: Basic search endpoint")
    try:
        url = "https://api.foursquare.com/v3/places/search"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        params = {
            'll': '40.7128,-74.0060',  # NYC coordinates
            'radius': 1000,
            'limit': 1
        }
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        print(f"  Status Code: {response.status_code}")
        print(f"  Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success! Found {len(data.get('results', []))} results")
            if data.get('results'):
                first_result = data['results'][0]
                print(f"  Sample business: {first_result.get('name', 'Unknown')}")
            return True
        elif response.status_code == 401:
            print("  ❌ 401 Unauthorized - API key issue")
            print(f"  Response: {response.text}")
            return False
        elif response.status_code == 403:
            print("  ❌ 403 Forbidden - Permission issue")
            print(f"  Response: {response.text}")
            return False
        elif response.status_code == 429:
            print("  ⚠️  429 Rate Limited - Too many requests")
            return False
        else:
            print(f"  ❌ Unexpected status: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Network error: {e}")
        return False

def test_api_permissions(api_key):
    """Test different API endpoints to check permissions."""
    print("\n🔐 Testing API Permissions")
    print("-" * 30)
    
    endpoints = [
        ("Places Search", "https://api.foursquare.com/v3/places/search"),
        ("Places Nearby", "https://api.foursquare.com/v3/places/nearby"),
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    
    for name, url in endpoints:
        try:
            params = {
                'll': '40.7128,-74.0060',
                'limit': 1
            }
            response = requests.get(url, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                print(f"  ✅ {name}: Working")
            elif response.status_code == 401:
                print(f"  ❌ {name}: 401 Unauthorized")
            elif response.status_code == 403:
                print(f"  ❌ {name}: 403 Forbidden")
            else:
                print(f"  ⚠️  {name}: Status {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {name}: Error - {e}")

def check_foursquare_api_version():
    """Check which Foursquare API version we're using."""
    print("\n📋 API Version Information")
    print("-" * 30)
    print("✓ Using Foursquare Places API v3")
    print("✓ Endpoint: https://api.foursquare.com/v3/")
    print("✓ Authentication: Bearer token")

def provide_troubleshooting_tips():
    """Provide troubleshooting tips for common issues."""
    print("\n🛠️  Troubleshooting Tips")
    print("-" * 30)
    print("1. API Key Issues:")
    print("   - Make sure you copied the FULL API key")
    print("   - Check for extra spaces or newlines")
    print("   - Verify the key is from the correct app")
    print()
    print("2. Foursquare Developer Portal:")
    print("   - Visit: https://developer.foursquare.com/")
    print("   - Go to 'My Apps' → Your App → API Keys")
    print("   - Use the 'API Key' (not Client ID or Client Secret)")
    print()
    print("3. App Configuration:")
    print("   - Ensure your app has the right permissions")
    print("   - Check if your app is active/approved")
    print("   - Verify you're not exceeding rate limits")
    print()
    print("4. Common Fixes:")
    print("   - Regenerate the API key")
    print("   - Create a new app if needed")
    print("   - Check Foursquare service status")

def main():
    """Main testing function."""
    print("🔑 Foursquare API Key Tester")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    if not api_key:
        print("❌ No API key found in .env file")
        print("Please add: FOURSQUARE_API_KEY=your_key_here")
        return
    
    # Test API key format
    if not test_api_key_format(api_key):
        print("\n❌ API key format issues detected")
        provide_troubleshooting_tips()
        return
    
    # Check API version info
    check_foursquare_api_version()
    
    # Test API connection
    if test_api_connection(api_key):
        print("\n🎉 SUCCESS! Your API key is working correctly!")
        print("You can now run the full BizRadar application:")
        print("  python main.py")
    else:
        print("\n❌ API key authentication failed")
        test_api_permissions(api_key)
        provide_troubleshooting_tips()
        
        print("\n🔄 Quick Fixes to Try:")
        print("1. Double-check your API key in .env file")
        print("2. Regenerate API key in Foursquare Developer Portal")
        print("3. Create a new app if the current one has issues")
        print("4. Wait a few minutes and try again (propagation delay)")

if __name__ == "__main__":
    main()
