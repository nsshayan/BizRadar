#!/usr/bin/env python3
"""
Component Testing Script for BizRadar

Test individual components and features without full application launch.
"""

import os
import sys
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_database_operations():
    """Test database functionality with sample data."""
    print("🗄️  Testing Database Operations")
    print("-" * 40)
    
    from bizradar.utils.database import DatabaseManager
    from bizradar.models.business import Business, Location
    from bizradar.models.monitoring import MonitoringSettings, Notification, NotificationType
    
    # Create test database
    db_manager = DatabaseManager("data/test_components.db")
    
    # Test business operations
    location = Location(latitude=40.7128, longitude=-74.0060, address="123 Test St")
    business = Business(
        fsq_id="test_001",
        name="Test Restaurant",
        categories=["Restaurant", "Italian"],
        location=location,
        rating=4.5,
        is_competitor=True
    )
    
    # Save and retrieve
    success = db_manager.save_business(business)
    print(f"✓ Save business: {'Success' if success else 'Failed'}")
    
    retrieved = db_manager.get_business("test_001")
    print(f"✓ Retrieve business: {'Success' if retrieved else 'Failed'}")
    if retrieved:
        print(f"  - Name: {retrieved.name}")
        print(f"  - Rating: {retrieved.rating}")
        print(f"  - Categories: {', '.join(retrieved.categories)}")
    
    # Test settings
    settings = MonitoringSettings(
        business_name="Test Business",
        business_location_lat=40.7128,
        business_location_lng=-74.0060,
        monitoring_radius=1000
    )
    
    settings_id = db_manager.save_monitoring_settings(settings)
    print(f"✓ Save settings: {'Success' if settings_id > 0 else 'Failed'}")
    
    # Test notifications
    notification = Notification(
        type=NotificationType.NEW_BUSINESS,
        title="Test Notification",
        message="This is a test notification"
    )
    
    notif_id = db_manager.save_notification(notification)
    print(f"✓ Save notification: {'Success' if notif_id > 0 else 'Failed'}")
    
    notifications = db_manager.get_notifications()
    print(f"✓ Retrieve notifications: {len(notifications)} found")
    
    print("✅ Database operations test complete\n")

def test_configuration():
    """Test configuration management."""
    print("⚙️  Testing Configuration")
    print("-" * 40)
    
    from bizradar.utils.config import Config
    
    # Test with demo environment
    os.environ['FOURSQUARE_API_KEY'] = 'demo_test_key_12345'
    os.environ['DEFAULT_RADIUS'] = '1500'
    
    config = Config()
    
    print(f"✓ API Key loaded: {'Yes' if config.foursquare_api_key else 'No'}")
    print(f"  - Key: {config.foursquare_api_key[:10]}..." if config.foursquare_api_key else "  - No key")
    print(f"✓ Default radius: {config.default_radius}m")
    print(f"✓ Scan interval: {config.scan_interval_minutes} minutes")
    print(f"✓ Database path: {config.database_path}")
    print(f"✓ Notifications enabled: {config.enable_notifications}")
    
    # Test validation
    is_configured = config.is_configured()
    print(f"✓ Configuration valid: {'Yes' if is_configured else 'No'}")
    
    # Test app info
    app_info = config.get_app_info()
    print(f"✓ App info: {app_info['name']} v{app_info['version']}")
    
    print("✅ Configuration test complete\n")

def test_models():
    """Test data models."""
    print("📊 Testing Data Models")
    print("-" * 40)
    
    from bizradar.models.business import Business, Location, BusinessHours
    from bizradar.models.monitoring import MonitoringSettings, Notification, NotificationType
    
    # Test Location model
    location = Location(
        latitude=40.7128,
        longitude=-74.0060,
        address="123 Main St",
        city="New York",
        state="NY"
    )
    
    location_dict = location.to_dict()
    location_restored = Location.from_dict(location_dict)
    print(f"✓ Location serialization: {'Success' if location_restored.address == location.address else 'Failed'}")
    
    # Test Business model
    business = Business(
        fsq_id="test_biz_001",
        name="Test Business",
        categories=["Restaurant", "Italian"],
        location=location,
        rating=4.5,
        verified=True
    )
    
    business_dict = business.to_dict()
    business_restored = Business.from_dict(business_dict)
    print(f"✓ Business serialization: {'Success' if business_restored.name == business.name else 'Failed'}")
    
    # Test distance calculation
    other_location = Location(latitude=40.7130, longitude=-74.0058)
    distance = business.distance_from(other_location)
    print(f"✓ Distance calculation: {distance:.3f} km")
    
    # Test MonitoringSettings
    settings = MonitoringSettings(
        business_name="Demo Business",
        business_location_lat=40.7128,
        business_location_lng=-74.0060,
        categories_to_monitor=["Restaurant", "Cafe"]
    )
    
    settings_dict = settings.to_dict()
    settings_restored = MonitoringSettings.from_dict(settings_dict)
    print(f"✓ Settings serialization: {'Success' if settings_restored.business_name == settings.business_name else 'Failed'}")
    
    # Test Notification
    notification = Notification(
        type=NotificationType.NEW_BUSINESS,
        title="Test Alert",
        message="New business detected",
        business_fsq_id="test_001"
    )
    
    notif_dict = notification.to_dict()
    notif_restored = Notification.from_dict(notif_dict)
    print(f"✓ Notification serialization: {'Success' if notif_restored.title == notification.title else 'Failed'}")
    
    print("✅ Data models test complete\n")

def test_mock_api():
    """Test mock API functionality."""
    print("🌐 Testing Mock API")
    print("-" * 40)
    
    # Import the mock client from demo_mode
    from demo_mode import MockFoursquareClient
    
    client = MockFoursquareClient("demo_key")
    
    # Test search
    places = client.search_nearby(40.7128, -74.0060, 1000)
    print(f"✓ Search nearby: {len(places)} businesses found")
    
    if places:
        first_place = places[0]
        print(f"  - First business: {first_place.name}")
        print(f"  - Categories: {', '.join(first_place.categories)}")
        print(f"  - Rating: {first_place.rating}")
        
        # Test place details
        details = client.get_place_details(first_place.fsq_id)
        print(f"✓ Place details: {'Success' if details else 'Failed'}")
        
        # Test trending
        trending = client.get_trending_places(40.7128, -74.0060)
        print(f"✓ Trending places: {len(trending)} found")
    
    print("✅ Mock API test complete\n")

def test_services():
    """Test service components."""
    print("🔧 Testing Services")
    print("-" * 40)
    
    from bizradar.utils.database import DatabaseManager
    from bizradar.services.notification_service import NotificationService
    from bizradar.models.monitoring import NotificationType
    from demo_mode import MockFoursquareClient
    
    # Setup
    db_manager = DatabaseManager("data/test_services.db")
    db_manager.initialize_database()
    
    # Test notification service
    notif_service = NotificationService(db_manager, enable_desktop_notifications=False)
    
    notif_id = notif_service.create_notification(
        NotificationType.NEW_BUSINESS,
        "Test Service Notification",
        "Testing notification service",
        send_desktop=False
    )
    
    print(f"✓ Create notification: {'Success' if notif_id > 0 else 'Failed'}")
    
    unread = notif_service.get_unread_notifications()
    print(f"✓ Get unread notifications: {len(unread)} found")
    
    summary = notif_service.get_notification_summary()
    print(f"✓ Notification summary: {summary['total_notifications']} total")
    
    print("✅ Services test complete\n")

def main():
    """Run all component tests."""
    print("🧪 BizRadar Component Testing")
    print("=" * 50)
    print("Testing individual components without full app launch\n")
    
    # Ensure test directories exist
    os.makedirs("data", exist_ok=True)
    
    try:
        test_configuration()
        test_models()
        test_database_operations()
        test_mock_api()
        test_services()
        
        print("🎉 All component tests completed successfully!")
        print("\nNext steps:")
        print("1. Run full demo: python demo_mode.py")
        print("2. Run unit tests: python run_tests.py")
        print("3. Launch full app: python main.py")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
