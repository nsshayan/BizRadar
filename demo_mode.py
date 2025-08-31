#!/usr/bin/env python3
"""
Demo Mode for BizRadar Application

This script runs BizRadar with mock data and simulated API responses,
allowing you to explore all features without a valid Foursquare API key.
"""

import os
import sys
import flet as ft
from datetime import datetime, timedelta
import random

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bizradar.models.business import Business, Location, BusinessHours
from bizradar.models.monitoring import MonitoringSettings, Notification, NotificationType, ScanHistory
from bizradar.utils.database import DatabaseManager
from bizradar.utils.config import Config

class MockFoursquareClient:
    """Mock Foursquare client that returns sample data."""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.sample_businesses = self._generate_sample_businesses()
    
    def _generate_sample_businesses(self):
        """Generate realistic sample business data."""
        businesses = [
            {
                "fsq_id": "demo_001",
                "name": "Tony's Italian Bistro",
                "categories": ["Restaurant", "Italian"],
                "location": {"latitude": 40.7128, "longitude": -74.0060, "address": "123 Main St"},
                "rating": 4.5,
                "verified": True,
                "popularity": 0.8
            },
            {
                "fsq_id": "demo_002", 
                "name": "Coffee Corner Cafe",
                "categories": ["Coffee Shop", "Cafe"],
                "location": {"latitude": 40.7130, "longitude": -74.0058, "address": "456 Oak Ave"},
                "rating": 4.2,
                "verified": True,
                "popularity": 0.7
            },
            {
                "fsq_id": "demo_003",
                "name": "Fresh Market Grocery",
                "categories": ["Grocery Store", "Market"],
                "location": {"latitude": 40.7125, "longitude": -74.0065, "address": "789 Pine St"},
                "rating": 3.8,
                "verified": False,
                "popularity": 0.6
            },
            {
                "fsq_id": "demo_004",
                "name": "Fitness First Gym",
                "categories": ["Gym", "Fitness Center"],
                "location": {"latitude": 40.7135, "longitude": -74.0055, "address": "321 Elm St"},
                "rating": 4.0,
                "verified": True,
                "popularity": 0.75
            },
            {
                "fsq_id": "demo_005",
                "name": "Quick Bites Food Truck",
                "categories": ["Food Truck", "Fast Food"],
                "location": {"latitude": 40.7132, "longitude": -74.0062, "address": "Mobile Location"},
                "rating": 4.3,
                "verified": False,
                "popularity": 0.9
            },
            {
                "fsq_id": "demo_006",
                "name": "Sunset Bar & Grill",
                "categories": ["Bar", "Restaurant", "American"],
                "location": {"latitude": 40.7120, "longitude": -74.0070, "address": "555 Sunset Blvd"},
                "rating": 4.1,
                "verified": True,
                "popularity": 0.65
            },
            {
                "fsq_id": "demo_007",
                "name": "Tech Repair Shop",
                "categories": ["Electronics", "Repair Service"],
                "location": {"latitude": 40.7140, "longitude": -74.0050, "address": "777 Tech Way"},
                "rating": 4.7,
                "verified": True,
                "popularity": 0.55
            },
            {
                "fsq_id": "demo_008",
                "name": "Bella's Beauty Salon",
                "categories": ["Beauty Salon", "Hair Salon"],
                "location": {"latitude": 40.7115, "longitude": -74.0075, "address": "888 Beauty Lane"},
                "rating": 4.4,
                "verified": True,
                "popularity": 0.7
            }
        ]
        return businesses
    
    def search_nearby(self, latitude, longitude, radius=1000, categories=None, limit=50):
        """Return mock search results."""
        from bizradar.api.foursquare_client import PlaceData
        
        results = []
        for biz in self.sample_businesses[:limit]:
            place = PlaceData(
                fsq_id=biz["fsq_id"],
                name=biz["name"],
                categories=biz["categories"],
                location=biz["location"],
                rating=biz["rating"],
                verified=biz["verified"],
                popularity=biz["popularity"]
            )
            results.append(place)
        
        return results
    
    def get_place_details(self, fsq_id):
        """Return mock place details."""
        from bizradar.api.foursquare_client import PlaceData
        
        for biz in self.sample_businesses:
            if biz["fsq_id"] == fsq_id:
                return PlaceData(
                    fsq_id=biz["fsq_id"],
                    name=biz["name"],
                    categories=biz["categories"],
                    location=biz["location"],
                    rating=biz["rating"],
                    verified=biz["verified"],
                    popularity=biz["popularity"]
                )
        return None
    
    def get_trending_places(self, latitude, longitude, radius=1000):
        """Return mock trending places."""
        trending = [biz for biz in self.sample_businesses if biz["popularity"] > 0.7]
        return [self.get_place_details(biz["fsq_id"]) for biz in trending]

def setup_demo_data(db_manager):
    """Populate database with demo data."""
    print("Setting up demo data...")
    
    # Create sample monitoring settings
    settings = MonitoringSettings(
        business_name="Demo Business",
        business_location_lat=40.7128,
        business_location_lng=-74.0060,
        monitoring_radius=1000,
        scan_interval_minutes=60,
        categories_to_monitor=["Restaurant", "Coffee Shop", "Retail"],
        notify_new_businesses=True,
        notify_rating_changes=True,
        notify_trending=True
    )
    db_manager.save_monitoring_settings(settings)
    
    # Create sample businesses
    sample_data = [
        ("demo_001", "Tony's Italian Bistro", ["Restaurant", "Italian"], 40.7128, -74.0060, "123 Main St", 4.5, True, True),
        ("demo_002", "Coffee Corner Cafe", ["Coffee Shop", "Cafe"], 40.7130, -74.0058, "456 Oak Ave", 4.2, False, True),
        ("demo_003", "Fresh Market Grocery", ["Grocery Store"], 40.7125, -74.0065, "789 Pine St", 3.8, False, False),
        ("demo_004", "Fitness First Gym", ["Gym", "Fitness"], 40.7135, -74.0055, "321 Elm St", 4.0, True, False),
        ("demo_005", "Quick Bites Food Truck", ["Food Truck"], 40.7132, -74.0062, "Mobile Location", 4.3, True, True),
        ("demo_006", "Sunset Bar & Grill", ["Bar", "Restaurant"], 40.7120, -74.0070, "555 Sunset Blvd", 4.1, False, True),
        ("demo_007", "Tech Repair Shop", ["Electronics", "Repair"], 40.7140, -74.0050, "777 Tech Way", 4.7, False, False),
        ("demo_008", "Bella's Beauty Salon", ["Beauty Salon"], 40.7115, -74.0075, "888 Beauty Lane", 4.4, True, False),
    ]
    
    for fsq_id, name, categories, lat, lng, address, rating, is_competitor, verified in sample_data:
        location = Location(latitude=lat, longitude=lng, address=address)
        business = Business(
            fsq_id=fsq_id,
            name=name,
            categories=categories,
            location=location,
            rating=rating,
            verified=verified,
            is_competitor=is_competitor,
            first_seen=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        db_manager.save_business(business)
    
    # Create sample notifications
    notifications_data = [
        (NotificationType.NEW_BUSINESS, "New Competitor Alert", "Quick Bites Food Truck has opened nearby", "demo_005", "Quick Bites Food Truck"),
        (NotificationType.RATING_CHANGE, "Rating Update", "Tony's Italian Bistro rating increased to 4.5 stars", "demo_001", "Tony's Italian Bistro"),
        (NotificationType.TRENDING_ACTIVITY, "Trending Business", "Coffee Corner Cafe is showing increased activity", "demo_002", "Coffee Corner Cafe"),
        (NotificationType.COMPETITOR_ALERT, "Monitoring Started", "Background monitoring is now active for your area", None, None),
    ]
    
    for i, (ntype, title, message, biz_id, biz_name) in enumerate(notifications_data):
        notification = Notification(
            type=ntype,
            title=title,
            message=message,
            business_fsq_id=biz_id,
            business_name=biz_name,
            created_at=datetime.now() - timedelta(hours=random.randint(1, 48)),
            read=(i % 2 == 0)  # Mark some as read
        )
        db_manager.save_notification(notification)
    
    # Create sample scan history
    for i in range(5):
        scan = ScanHistory(
            scan_timestamp=datetime.now() - timedelta(hours=i*2),
            businesses_found=random.randint(5, 12),
            new_businesses=random.randint(0, 2),
            updated_businesses=random.randint(0, 3),
            scan_duration_seconds=random.uniform(2.5, 8.0),
            success=True
        )
        db_manager.save_scan_history(scan)
    
    print("✓ Demo data setup complete!")

def main(page: ft.Page):
    """Main demo application entry point."""
    # Setup demo environment
    os.environ['FOURSQUARE_API_KEY'] = 'demo_key_12345'
    
    # Initialize components
    config = Config()
    db_manager = DatabaseManager("data/bizradar_demo.db")
    db_manager.initialize_database()
    
    # Setup demo data
    setup_demo_data(db_manager)
    
    # Create mock services
    mock_client = MockFoursquareClient("demo_key")
    
    # Import and setup the main app with mock client
    from bizradar.gui.main_app import BizRadarApp
    from bizradar.services.monitoring_service import MonitoringService
    from bizradar.services.notification_service import NotificationService
    
    app = BizRadarApp(page, config, db_manager)
    
    # Replace with mock services
    app.foursquare_client = mock_client
    app.monitoring_service = MonitoringService(mock_client, db_manager)
    app.notification_service = NotificationService(db_manager, config.enable_notifications)
    
    # Build the app
    app.build()
    
    # Show demo info
    page.snack_bar = ft.SnackBar(
        content=ft.Text("🎯 DEMO MODE: Explore BizRadar with sample data!"),
        bgcolor=ft.Colors.GREEN_600
    )
    page.snack_bar.open = True
    page.update()

if __name__ == "__main__":
    print("🎯 Starting BizRadar in DEMO MODE")
    print("=" * 50)
    print("This demo includes:")
    print("✓ Sample business data")
    print("✓ Mock API responses") 
    print("✓ Simulated notifications")
    print("✓ Full UI functionality")
    print("✓ No API key required")
    print("=" * 50)
    
    # Ensure demo data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Run the demo app
    ft.app(target=main, view=ft.WEB_BROWSER, port=8081)
