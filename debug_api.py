#!/usr/bin/env python3
"""
Debug Foursquare API Issues

Test the API key directly and show detailed error information.
"""

import os
import requests
from dotenv import load_dotenv

def test_api_directly():
    """Test the API key directly with detailed error reporting."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')

    print("🔍 Direct API Test")
    print("=" * 30)
    print(f"API Key: {api_key}")
    print(f"API Key Length: {len(api_key)}")
    print(f"API Key Preview: {api_key[:15]}...{api_key[-10:]}")
    print()

    # Test the correct new API URL with version
    url = "https://places-api.foursquare.com/places/search"
    print(f"🌐 Testing New API: {url}")
    test_single_url(api_key, url)
    print()

def test_single_url(api_key, url):
    """Test a single URL endpoint."""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    params = {
        'll': '40.7128,-74.0060',  # NYC
        'radius': 1000,
        'limit': 1,
        'version': 'v1'  # Required for new API
    }

    print(f"Headers: {headers}")
    print(f"Params: {params}")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")

        if response.status_code == 200:
            print("✅ SUCCESS! This URL works!")
            data = response.json()
            print(f"Results found: {len(data.get('results', []))}")
            return True
        elif response.status_code == 401:
            print("❌ 401 UNAUTHORIZED")
        elif response.status_code == 403:
            print("❌ 403 FORBIDDEN")
        elif response.status_code == 404:
            print("❌ 404 NOT FOUND - Wrong URL")
        else:
            print(f"❌ Status code: {response.status_code}")

    except Exception as e:
        print(f"❌ Request failed: {e}")

    return False

def show_correct_api_key_format():
    """Show what a correct Foursquare API key should look like."""
    print("\n📋 Correct Foursquare API Key Format")
    print("=" * 40)
    print("A valid Foursquare API key should:")
    print("✓ Start with 'fsq3'")
    print("✓ Be around 40-50 characters long")
    print("✓ Contain only alphanumeric characters and underscores")
    print("✓ NOT contain: / + = (these suggest base64 encoding)")
    print()
    print("Example format: fsq3abcdef1234567890abcdef1234567890abcd")
    print()
    print("Your current key contains '/' and '=' which suggests:")
    print("1. You might have copied a base64-encoded version")
    print("2. You might have copied the wrong field")
    print("3. There might be encoding issues")

def provide_step_by_step_fix():
    """Provide step-by-step instructions to get the correct API key."""
    print("\n🛠️  Step-by-Step Fix")
    print("=" * 25)
    print("1. Go to https://developer.foursquare.com/")
    print("2. Sign in to your account")
    print("3. Click 'My Apps' in the top navigation")
    print("4. Click on your app name")
    print("5. Look for 'API Keys' section")
    print("6. Copy the 'API Key' field (NOT Client ID or Client Secret)")
    print("7. The key should start with 'fsq3'")
    print("8. Paste it in your .env file without quotes")
    print()
    print("If you don't see an API key starting with 'fsq3':")
    print("- Try regenerating the key")
    print("- Create a new app")
    print("- Make sure your app is approved/active")

def main():
    """Main debug function."""
    print("🐛 Foursquare API Debug Tool")
    print("=" * 35)
    
    # Test current API key
    test_api_directly()
    
    # Show correct format
    show_correct_api_key_format()
    
    # Provide fix instructions
    provide_step_by_step_fix()

if __name__ == "__main__":
    main()
