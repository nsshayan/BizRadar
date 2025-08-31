#!/usr/bin/env python3
"""
Test different version formats for Foursquare Places API.
"""

import os
import requests
from dotenv import load_dotenv

def test_version_formats():
    """Test different version formats to find the correct one."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🔍 Testing Different Version Formats")
    print("=" * 40)
    
    # Different version formats to test
    version_formats = [
        "v2025-06-17",
        "2025-06-17", 
        "20250617",
        "v1",
        "1",
        "latest",
        None,  # No version parameter
        "",    # Empty version
    ]
    
    base_url = "https://places-api.foursquare.com/places/search"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    base_params = {
        "ll": "40.7128,-74.0060",
        "radius": 1000,
        "limit": 1
    }
    
    successful_versions = []
    
    for i, version in enumerate(version_formats, 1):
        print(f"🧪 Test {i}: Version = {version if version is not None else 'None'}")
        
        # Prepare params
        params = base_params.copy()
        if version is not None and version != "":
            params["version"] = version
        
        try:
            response = requests.get(base_url, headers=headers, params=params, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                try:
                    data = response.json()
                    if 'results' in data:
                        results = data['results']
                        print(f"   Found {len(results)} results")
                        if results:
                            print(f"   Sample: {results[0].get('name', 'Unknown')}")
                    successful_versions.append(version)
                except Exception as e:
                    print(f"   JSON error: {e}")
            elif response.status_code == 400:
                print(f"   ❌ 400 BAD REQUEST: {response.text[:100]}...")
            elif response.status_code == 401:
                print("   ❌ 401 UNAUTHORIZED")
            elif response.status_code == 404:
                print("   ❌ 404 NOT FOUND")
            else:
                print(f"   ❌ Status {response.status_code}: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    return successful_versions

def test_alternative_auth_methods():
    """Test different authentication methods."""
    load_dotenv()
    api_key = os.getenv('FOURSQUARE_API_KEY')
    
    print("🔐 Testing Alternative Authentication Methods")
    print("=" * 50)
    
    auth_methods = [
        {
            "name": "Bearer Token in Header",
            "headers": {"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1}
        },
        {
            "name": "API Key in Query Parameter",
            "headers": {"Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1, "api_key": api_key}
        },
        {
            "name": "API Key as Authorization Header",
            "headers": {"Authorization": api_key, "Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1}
        },
        {
            "name": "X-API-Key Header",
            "headers": {"X-API-Key": api_key, "Accept": "application/json"},
            "params": {"ll": "40.7128,-74.0060", "radius": 1000, "limit": 1}
        }
    ]
    
    base_url = "https://places-api.foursquare.com/places/search"
    
    for i, method in enumerate(auth_methods, 1):
        print(f"🔑 Test {i}: {method['name']}")
        
        try:
            response = requests.get(base_url, headers=method['headers'], params=method['params'], timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SUCCESS!")
                try:
                    data = response.json()
                    if 'results' in data:
                        print(f"   Found {len(data['results'])} results")
                except:
                    pass
            else:
                print(f"   Response: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   Error: {e}")
        
        print()

def check_api_documentation():
    """Try to get API documentation or help."""
    print("📚 Checking API Documentation Endpoints")
    print("=" * 45)
    
    doc_urls = [
        "https://places-api.foursquare.com/",
        "https://places-api.foursquare.com/docs",
        "https://places-api.foursquare.com/help",
        "https://places-api.foursquare.com/version",
        "https://places-api.foursquare.com/places"
    ]
    
    for url in doc_urls:
        print(f"Checking: {url}")
        try:
            response = requests.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  Content preview: {response.text[:200]}...")
            else:
                print(f"  Response: {response.text[:100]}...")
        except Exception as e:
            print(f"  Error: {e}")
        print()

def main():
    """Main test function."""
    print("🚀 Foursquare API Version Format Tester")
    print("=" * 50)
    
    successful_versions = test_version_formats()
    
    if successful_versions:
        print("🎉 WORKING VERSION FORMATS FOUND!")
        print("=" * 40)
        for version in successful_versions:
            print(f"✅ Version: {version if version is not None else 'No version parameter'}")
    else:
        print("❌ No working version formats found")
        print("Testing alternative authentication methods...")
        test_alternative_auth_methods()
        
        print("Checking documentation endpoints...")
        check_api_documentation()

if __name__ == "__main__":
    main()
