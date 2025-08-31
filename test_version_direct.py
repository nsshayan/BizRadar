#!/usr/bin/env python3
"""
Test version formats directly with the new Places API.
"""

import os
import requests
from dotenv import load_dotenv

def test_version_direct():
    """Test version formats directly."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🔍 Testing Version Formats with New Places API")
    print("=" * 50)
    
    # Version formats to test based on documentation
    versions = [
        "2025-06-17",
        "20250617", 
        "v2025-06-17",
        "2024-12-01",
        "2024-01-01",
        "latest",
        "v1",
        "1.0",
        None
    ]
    
    url = "https://places-api.foursquare.com/places/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    base_params = {
        "ll": "40.7128,-74.0060",
        "radius": 1000,
        "limit": 1
    }
    
    for version in versions:
        print(f"🧪 Testing version: {version}")
        
        params = base_params.copy()
        if version is not None:
            params["version"] = version
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                data = response.json()
                print(f"   Response keys: {list(data.keys())}")
                if 'results' in data:
                    print(f"   Found {len(data['results'])} results")
                elif 'places' in data:
                    print(f"   Found {len(data['places'])} places")
                return version
            else:
                print(f"   Response: {response.text[:150]}...")
                
        except Exception as e:
            print(f"   Error: {e}")
        
        print()
    
    return None

def test_different_endpoints():
    """Test different endpoint variations."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🎯 Testing Different Endpoint Variations")
    print("=" * 45)
    
    endpoints = [
        "https://places-api.foursquare.com/places/search",
        "https://places-api.foursquare.com/places/nearby", 
        "https://places-api.foursquare.com/v1/places/search",
        "https://places-api.foursquare.com/v2/places/search",
        "https://api.foursquare.com/places/search",
        "https://api.foursquare.com/v4/places/search"
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    params = {
        "ll": "40.7128,-74.0060",
        "radius": 1000,
        "limit": 1,
        "version": "2025-06-17"
    }
    
    for endpoint in endpoints:
        print(f"Testing: {endpoint}")
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✅ SUCCESS!")
                data = response.json()
                print(f"  Response keys: {list(data.keys())}")
                return endpoint
            elif response.status_code == 404:
                print("  ❌ 404 - Endpoint not found")
            else:
                print(f"  Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"  Error: {e}")
        print()
    
    return None

def main():
    """Main test function."""
    print("🚀 Direct API Version Testing")
    print("=" * 35)
    
    # Test version formats
    working_version = test_version_direct()
    
    if working_version:
        print(f"🎉 WORKING VERSION FOUND: {working_version}")
    else:
        print("❌ No working version found, testing endpoints...")
        working_endpoint = test_different_endpoints()
        
        if working_endpoint:
            print(f"🎉 WORKING ENDPOINT FOUND: {working_endpoint}")
        else:
            print("❌ No working configuration found")
            print("\nPossible issues:")
            print("1. API key type mismatch (Legacy vs New)")
            print("2. API version not yet available")
            print("3. Account permissions issue")
            print("4. API endpoint changes")

if __name__ == "__main__":
    main()
