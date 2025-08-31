#!/usr/bin/env python3
"""
Check BizRadar Configuration

Verifies .env file setup and configuration.
"""

import os
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and is properly formatted."""
    print("📁 Checking .env File")
    print("-" * 25)
    
    if not os.path.exists('.env'):
        print("❌ .env file not found")
        print("Creating .env file from template...")
        
        if os.path.exists('.env.example'):
            import shutil
            shutil.copy('.env.example', '.env')
            print("✅ Created .env file from .env.example")
            print("Please edit .env file and add your Foursquare API key")
        else:
            # Create basic .env file
            with open('.env', 'w') as f:
                f.write("# Foursquare API Configuration\n")
                f.write("FOURSQUARE_API_KEY=your_foursquare_api_key_here\n")
                f.write("\n# Application Configuration\n")
                f.write("DEFAULT_RADIUS=1000\n")
                f.write("SCAN_INTERVAL_MINUTES=60\n")
            print("✅ Created basic .env file")
            print("Please edit .env file and add your Foursquare API key")
        return False
    
    print("✅ .env file exists")
    
    # Check file content
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        if 'FOURSQUARE_API_KEY=' in content:
            print("✅ FOURSQUARE_API_KEY found in .env")
            
            # Check if it's still the placeholder
            if 'your_foursquare_api_key_here' in content:
                print("⚠️  API key is still set to placeholder")
                return False
            else:
                print("✅ API key appears to be configured")
                return True
        else:
            print("❌ FOURSQUARE_API_KEY not found in .env")
            return False
            
    except Exception as e:
        print(f"❌ Error reading .env file: {e}")
        return False

def check_loaded_config():
    """Check loaded configuration values."""
    print("\n⚙️  Checking Loaded Configuration")
    print("-" * 35)
    
    load_dotenv()
    
    api_key = os.getenv('FOURSQUARE_API_KEY')
    if api_key:
        print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '***'}")
    else:
        print("❌ API Key not loaded")
        return False
    
    # Check other config values
    radius = os.getenv('DEFAULT_RADIUS', '1000')
    interval = os.getenv('SCAN_INTERVAL_MINUTES', '60')
    
    print(f"✅ Default radius: {radius}m")
    print(f"✅ Scan interval: {interval} minutes")
    
    return True

def show_env_file_format():
    """Show the correct .env file format."""
    print("\n📝 Correct .env File Format")
    print("-" * 30)
    print("Your .env file should look like this:")
    print()
    print("# Foursquare API Configuration")
    print("FOURSQUARE_API_KEY=fsq3abcd1234567890...")
    print()
    print("# Application Configuration (optional)")
    print("DEFAULT_RADIUS=1000")
    print("SCAN_INTERVAL_MINUTES=60")
    print("ENABLE_NOTIFICATIONS=true")
    print()
    print("Important notes:")
    print("- No spaces around the = sign")
    print("- No quotes around the values")
    print("- API key should be the full key from Foursquare")

def main():
    """Main configuration check."""
    print("🔧 BizRadar Configuration Checker")
    print("=" * 40)
    
    # Check .env file
    env_ok = check_env_file()
    
    if env_ok:
        # Check loaded configuration
        config_ok = check_loaded_config()
        
        if config_ok:
            print("\n🎉 Configuration looks good!")
            print("Next step: Test your API key")
            print("Run: python test_api_key.py")
        else:
            print("\n❌ Configuration issues found")
            show_env_file_format()
    else:
        print("\n❌ .env file issues found")
        show_env_file_format()
        
        print("\n🔄 Steps to fix:")
        print("1. Edit the .env file")
        print("2. Replace 'your_foursquare_api_key_here' with your actual API key")
        print("3. Save the file")
        print("4. Run this script again to verify")

if __name__ == "__main__":
    main()
