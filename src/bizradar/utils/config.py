"""
Configuration management for BizRadar application.

Handles loading and managing application configuration from environment variables and defaults.
"""

import os
from typing import Optional
from dotenv import load_dotenv

class Config:
    """Application configuration manager."""
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        # API Configuration
        self.foursquare_api_key = os.getenv('FOURSQUARE_API_KEY', '')
        
        # Application Configuration
        self.default_radius = int(os.getenv('DEFAULT_RADIUS', '1000'))
        self.scan_interval_minutes = int(os.getenv('SCAN_INTERVAL_MINUTES', '60'))
        self.max_results_per_scan = int(os.getenv('MAX_RESULTS_PER_SCAN', '50'))
        
        # Database Configuration
        self.database_path = os.getenv('DATABASE_PATH', 'data/bizradar.db')
        
        # Notification Settings
        self.enable_notifications = os.getenv('ENABLE_NOTIFICATIONS', 'true').lower() == 'true'
        self.notification_sound = os.getenv('NOTIFICATION_SOUND', 'true').lower() == 'true'
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.database_path), exist_ok=True)
    
    def is_configured(self) -> bool:
        """Check if the application is properly configured."""
        return bool(self.foursquare_api_key)
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is present and has the correct format."""
        if not self.foursquare_api_key:
            return False
        
        # Basic validation - Foursquare API keys are typically long alphanumeric strings
        return len(self.foursquare_api_key) > 20 and self.foursquare_api_key.replace('-', '').replace('_', '').isalnum()
    
    def update_api_key(self, api_key: str) -> bool:
        """Update the API key and save to environment."""
        self.foursquare_api_key = api_key
        
        # Update .env file if it exists
        env_path = '.env'
        if os.path.exists(env_path):
            try:
                # Read existing .env content
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                # Update or add the API key line
                updated = False
                for i, line in enumerate(lines):
                    if line.startswith('FOURSQUARE_API_KEY='):
                        lines[i] = f'FOURSQUARE_API_KEY={api_key}\n'
                        updated = True
                        break
                
                if not updated:
                    lines.append(f'FOURSQUARE_API_KEY={api_key}\n')
                
                # Write back to file
                with open(env_path, 'w') as f:
                    f.writelines(lines)
                
                return True
            except Exception:
                return False
        else:
            # Create new .env file
            try:
                with open(env_path, 'w') as f:
                    f.write(f'FOURSQUARE_API_KEY={api_key}\n')
                return True
            except Exception:
                return False
    
    def get_app_info(self) -> dict:
        """Get application information for display."""
        return {
            'name': 'BizRadar',
            'version': '1.0.0',
            'description': 'Business Monitoring Application',
            'configured': self.is_configured(),
            'database_path': self.database_path,
            'default_radius': self.default_radius,
            'scan_interval': self.scan_interval_minutes
        }
