#!/usr/bin/env python3
"""
Setup script for BizRadar application.

Handles installation, dependency checking, and initial configuration.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        print(f"Current version: {sys.version}")
        return False
    print(f"✓ Python version {sys.version.split()[0]} is compatible")
    return True

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories."""
    directories = ["data", "logs"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def setup_environment():
    """Set up environment configuration."""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✓ Created .env file from template")
        print("  Please edit .env file with your Foursquare API key")
    elif env_file.exists():
        print("✓ .env file already exists")
    else:
        print("⚠ No .env.example file found")

def run_tests():
    """Run basic tests to verify installation."""
    print("Running basic tests...")
    try:
        result = subprocess.run([sys.executable, "run_tests.py"], 
                              capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print("✓ Basic tests passed")
            return True
        else:
            print("⚠ Some tests failed, but installation can continue")
            print("Test output:", result.stdout[-200:])  # Show last 200 chars
            return True  # Don't fail setup for test failures
    except subprocess.TimeoutExpired:
        print("⚠ Tests timed out, but installation can continue")
        return True
    except Exception as e:
        print(f"⚠ Could not run tests: {e}")
        return True

def check_api_key():
    """Check if API key is configured."""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if "FOURSQUARE_API_KEY=your_foursquare_api_key_here" in content:
                print("⚠ Please update your Foursquare API key in .env file")
                return False
            elif "FOURSQUARE_API_KEY=" in content:
                print("✓ API key appears to be configured")
                return True
    print("⚠ No .env file found - API key needs to be configured")
    return False

def main():
    """Main setup function."""
    print("="*50)
    print("BizRadar Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies. Please check your internet connection and try again.")
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Run tests
    run_tests()
    
    # Check API key
    api_configured = check_api_key()
    
    print("\n" + "="*50)
    print("Setup Complete!")
    print("="*50)
    
    if api_configured:
        print("✓ BizRadar is ready to use!")
        print("  Run: python main.py")
    else:
        print("⚠ Setup complete, but API key needs configuration:")
        print("  1. Get API key from: https://developer.foursquare.com/")
        print("  2. Edit .env file and add your API key")
        print("  3. Run: python main.py")
    
    print("\nAdditional commands:")
    print("  Run tests: python run_tests.py")
    print("  View logs: check the logs/ directory")

if __name__ == "__main__":
    main()
