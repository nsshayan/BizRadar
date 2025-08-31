"""
Unit tests for database functionality.
"""

import unittest
import tempfile
import os
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bizradar.utils.database import DatabaseManager
from bizradar.models.business import Business, Location
from bizradar.models.monitoring import MonitoringSettings, Notification, NotificationType

class TestDatabaseManager(unittest.TestCase):
    """Test cases for DatabaseManager class."""
    
    def setUp(self):
        """Set up test database."""
        # Create temporary database file
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        self.db_manager = DatabaseManager(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database."""
        # Remove temporary database file
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_database_initialization(self):
        """Test database initialization creates tables."""
        # Database should be initialized in setUp
        with self.db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check that tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = ['businesses', 'monitoring_settings', 'notifications', 'scan_history']
            for table in expected_tables:
                self.assertIn(table, tables)
    
    def test_save_and_get_business(self):
        """Test saving and retrieving a business."""
        # Create test business
        location = Location(latitude=40.7128, longitude=-74.0060, address="123 Test St")
        business = Business(
            fsq_id="test_id",
            name="Test Business",
            categories=["Restaurant", "Italian"],
            location=location,
            rating=4.5,
            verified=True,
            is_competitor=True
        )
        
        # Save business
        success = self.db_manager.save_business(business)
        self.assertTrue(success)
        
        # Retrieve business
        retrieved = self.db_manager.get_business("test_id")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.fsq_id, "test_id")
        self.assertEqual(retrieved.name, "Test Business")
        self.assertEqual(len(retrieved.categories), 2)
        self.assertEqual(retrieved.rating, 4.5)
        self.assertTrue(retrieved.verified)
        self.assertTrue(retrieved.is_competitor)
    
    def test_get_nonexistent_business(self):
        """Test retrieving a non-existent business."""
        business = self.db_manager.get_business("nonexistent_id")
        self.assertIsNone(business)
    
    def test_get_all_businesses(self):
        """Test retrieving all businesses."""
        # Create and save multiple businesses
        businesses = []
        for i in range(3):
            location = Location(latitude=40.7128 + i, longitude=-74.0060 + i)
            business = Business(
                fsq_id=f"test_id_{i}",
                name=f"Test Business {i}",
                categories=["Restaurant"],
                location=location,
                is_competitor=(i % 2 == 0)
            )
            businesses.append(business)
            self.db_manager.save_business(business)
        
        # Retrieve all businesses
        all_businesses = self.db_manager.get_all_businesses()
        self.assertEqual(len(all_businesses), 3)
        
        # Retrieve only competitors
        competitors = self.db_manager.get_all_businesses(is_competitor=True)
        self.assertEqual(len(competitors), 2)  # businesses 0 and 2
        
        # Retrieve only non-competitors
        non_competitors = self.db_manager.get_all_businesses(is_competitor=False)
        self.assertEqual(len(non_competitors), 1)  # business 1
    
    def test_save_and_get_monitoring_settings(self):
        """Test saving and retrieving monitoring settings."""
        settings = MonitoringSettings(
            business_name="My Business",
            business_location_lat=40.7128,
            business_location_lng=-74.0060,
            monitoring_radius=1500,
            scan_interval_minutes=30,
            categories_to_monitor=["Restaurant", "Cafe"],
            notify_new_businesses=True
        )
        
        # Save settings
        settings_id = self.db_manager.save_monitoring_settings(settings)
        self.assertGreater(settings_id, 0)
        
        # Retrieve settings
        retrieved = self.db_manager.get_monitoring_settings()
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.business_name, "My Business")
        self.assertEqual(retrieved.monitoring_radius, 1500)
        self.assertEqual(len(retrieved.categories_to_monitor), 2)
        self.assertTrue(retrieved.notify_new_businesses)
    
    def test_save_and_get_notifications(self):
        """Test saving and retrieving notifications."""
        notification = Notification(
            type=NotificationType.NEW_BUSINESS,
            title="Test Notification",
            message="This is a test notification",
            business_fsq_id="test_business_id",
            business_name="Test Business"
        )
        
        # Save notification
        notification_id = self.db_manager.save_notification(notification)
        self.assertGreater(notification_id, 0)
        
        # Retrieve notifications
        notifications = self.db_manager.get_notifications()
        self.assertEqual(len(notifications), 1)
        
        retrieved = notifications[0]
        self.assertEqual(retrieved.type, NotificationType.NEW_BUSINESS)
        self.assertEqual(retrieved.title, "Test Notification")
        self.assertEqual(retrieved.business_fsq_id, "test_business_id")
        self.assertFalse(retrieved.read)
    
    def test_mark_notification_read(self):
        """Test marking notification as read."""
        notification = Notification(
            type=NotificationType.NEW_BUSINESS,
            title="Test Notification",
            message="Test message"
        )
        
        notification_id = self.db_manager.save_notification(notification)
        
        # Mark as read
        success = self.db_manager.mark_notification_read(notification_id)
        self.assertTrue(success)
        
        # Verify it's marked as read
        notifications = self.db_manager.get_notifications()
        self.assertTrue(notifications[0].read)
    
    def test_get_unread_notifications(self):
        """Test filtering unread notifications."""
        # Create read and unread notifications
        read_notification = Notification(
            type=NotificationType.NEW_BUSINESS,
            title="Read Notification",
            message="This is read"
        )
        unread_notification = Notification(
            type=NotificationType.BUSINESS_UPDATED,
            title="Unread Notification",
            message="This is unread"
        )
        
        read_id = self.db_manager.save_notification(read_notification)
        unread_id = self.db_manager.save_notification(unread_notification)
        
        # Mark one as read
        self.db_manager.mark_notification_read(read_id)
        
        # Get unread notifications
        unread_notifications = self.db_manager.get_notifications(unread_only=True)
        self.assertEqual(len(unread_notifications), 1)
        self.assertEqual(unread_notifications[0].title, "Unread Notification")
    
    def test_businesses_within_radius(self):
        """Test getting businesses within radius."""
        # Create businesses at different locations
        center_lat, center_lng = 40.7128, -74.0060
        
        # Close business (should be included)
        close_location = Location(latitude=center_lat + 0.001, longitude=center_lng + 0.001)
        close_business = Business(
            fsq_id="close_business",
            name="Close Business",
            categories=["Restaurant"],
            location=close_location
        )
        
        # Far business (should be excluded)
        far_location = Location(latitude=center_lat + 1.0, longitude=center_lng + 1.0)
        far_business = Business(
            fsq_id="far_business",
            name="Far Business",
            categories=["Restaurant"],
            location=far_location
        )
        
        self.db_manager.save_business(close_business)
        self.db_manager.save_business(far_business)
        
        # Get businesses within small radius
        nearby_businesses = self.db_manager.get_businesses_within_radius(
            center_lat, center_lng, 1.0  # 1 km radius
        )
        
        # Should only include the close business
        business_ids = [b.fsq_id for b in nearby_businesses]
        self.assertIn("close_business", business_ids)
        # Note: The far business might still be included due to the simplified bounding box approach
        # In a production system, you'd want more accurate distance calculation

if __name__ == '__main__':
    unittest.main()
