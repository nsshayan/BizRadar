#!/usr/bin/env python3
"""
Test Foursquare API with new version v2025-06-17

Test the latest API configuration with the new version and base URL.
"""

import os
import requests
from dotenv import load_dotenv

def test_new_api_version():
    """Test the new API version v2025-06-17."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🔍 Testing Foursquare API v2025-06-17")
    print("=" * 45)
    print(f"API Key: {api_key}")
    print(f"Key Length: {len(api_key)}")
    print(f"Key Preview: {api_key[:10]}...{api_key[-4:]}")
    print()
    
    # Test configurations for the new API version
    test_configs = [
        {
            "name": "New Places API v2025-06-17",
            "url": "https://places-api.foursquare.com/places/search",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            },
            "params": {
                "ll": "40.7128,-74.0060",
                "radius": 1000,
                "limit": 5,
                "version": "v2025-06-17"
            }
        },
        {
            "name": "Legacy API v3 with Bearer",
            "url": "https://api.foursquare.com/v3/places/search",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            },
            "params": {
                "ll": "40.7128,-74.0060",
                "radius": 1000,
                "limit": 5
            }
        },
        {
            "name": "Places API with query param auth",
            "url": "https://places-api.foursquare.com/places/search",
            "headers": {
                "Accept": "application/json"
            },
            "params": {
                "ll": "40.7128,-74.0060",
                "radius": 1000,
                "limit": 5,
                "version": "v2025-06-17",
                "api_key": api_key
            }
        },
        {
            "name": "Places API nearby endpoint",
            "url": "https://places-api.foursquare.com/places/nearby",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json"
            },
            "params": {
                "ll": "40.7128,-74.0060",
                "radius": 1000,
                "limit": 5,
                "version": "v2025-06-17"
            }
        }
    ]
    
    successful_configs = []
    
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
                timeout=15
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                try:
                    data = response.json()
                    
                    # Handle different response formats
                    if 'results' in data:
                        results = data['results']
                        print(f"   Found {len(results)} results")
                        if results:
                            first_result = results[0]
                            print(f"   Sample: {first_result.get('name', 'Unknown')}")
                            print(f"   Categories: {[cat.get('name', '') for cat in first_result.get('categories', [])]}")
                    elif 'places' in data:
                        places = data['places']
                        print(f"   Found {len(places)} places")
                        if places:
                            print(f"   Sample: {places[0].get('name', 'Unknown')}")
                    else:
                        print(f"   Response keys: {list(data.keys())}")
                    
                    successful_configs.append(config)
                    
                except Exception as json_error:
                    print(f"   ⚠️  JSON parse error: {json_error}")
                    print(f"   Raw response: {response.text[:200]}...")
                    
            elif response.status_code == 401:
                print("   ❌ 401 UNAUTHORIZED - API key issue")
            elif response.status_code == 403:
                print("   ❌ 403 FORBIDDEN - Permission issue")
            elif response.status_code == 404:
                print("   ❌ 404 NOT FOUND - Wrong endpoint")
            elif response.status_code == 400:
                print("   ❌ 400 BAD REQUEST")
                print(f"   Response: {response.text[:200]}...")
            else:
                print(f"   ❌ Status {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print("   ❌ Request timeout")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {e}")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
        
        print()
    
    return successful_configs

def test_specific_endpoints():
    """Test specific endpoints that might work with the new API."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🎯 Testing Specific Endpoints")
    print("=" * 35)
    
    # Test different endpoint variations
    endpoints = [
        "https://places-api.foursquare.com/places/search",
        "https://places-api.foursquare.com/places/nearby",
        "https://places-api.foursquare.com/v1/places/search",
        "https://api.foursquare.com/v3/places/search",
        "https://api.foursquare.com/places/search"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    params = {
        "ll": "40.7128,-74.0060",
        "radius": 1000,
        "limit": 1,
        "version": "v2025-06-17"
    }
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print("  ✅ SUCCESS!")
                break
            else:
                print(f"  Response: {response.text[:100]}...")
        except Exception as e:
            print(f"  Error: {e}")
        print()

def main():
    """Main test function."""
    print("🚀 Foursquare API v2025-06-17 Tester")
    print("=" * 50)
    
    successful_configs = test_new_api_version()
    
    print("🎯 Testing Additional Endpoints")
    print("=" * 35)
    test_specific_endpoints()
    
    if successful_configs:
        print("🎉 WORKING CONFIGURATIONS FOUND!")
        print("=" * 40)
        for i, config in enumerate(successful_configs, 1):
            print(f"{i}. {config['name']}")
            print(f"   URL: {config['url']}")
            print(f"   Method: {'Bearer token' if 'Authorization' in config['headers'] else 'Query param'}")
        
        print("\n✅ BizRadar will be updated with the working configuration!")
    else:
        print("❌ NO WORKING CONFIGURATIONS FOUND")
        print("=" * 40)
        print("Possible next steps:")
        print("1. Verify API key is correct and active")
        print("2. Check Foursquare developer portal for latest API docs")
        print("3. Try creating a new app/API key")
        print("4. Contact Foursquare support if needed")

if __name__ == "__main__":
    main()
