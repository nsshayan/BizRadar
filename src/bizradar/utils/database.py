"""
Database management for BizRadar application.

Handles SQLite database operations for storing businesses, monitoring settings, and notifications.
"""

import sqlite3
import json
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from contextlib import contextmanager

from ..models.business import Business, Location, BusinessHours
from ..models.monitoring import MonitoringSettings, Notification, ScanHistory, NotificationType, MonitoringStatus

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages all database operations for BizRadar."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        try:
            yield conn
        finally:
            conn.close()
    
    def init_db(self):
        """Initialize the database with required tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create businesses table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS businesses (
                    fsq_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    categories TEXT NOT NULL,
                    location_data TEXT NOT NULL,
                    rating REAL,
                    hours_data TEXT,
                    website TEXT,
                    phone TEXT,
                    verified BOOLEAN DEFAULT FALSE,
                    popularity REAL,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_competitor BOOLEAN DEFAULT FALSE,
                    notes TEXT
                )
            ''')
            
            # Create monitoring_settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monitoring_settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    business_name TEXT NOT NULL,
                    business_location_lat REAL NOT NULL,
                    business_location_lng REAL NOT NULL,
                    monitoring_radius INTEGER DEFAULT 1000,
                    scan_interval_minutes INTEGER DEFAULT 60,
                    categories_to_monitor TEXT,
                    exclude_categories TEXT,
                    min_rating_threshold REAL,
                    notify_new_businesses BOOLEAN DEFAULT TRUE,
                    notify_rating_changes BOOLEAN DEFAULT TRUE,
                    notify_trending BOOLEAN DEFAULT TRUE,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    business_fsq_id TEXT,
                    business_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    read BOOLEAN DEFAULT FALSE,
                    dismissed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (business_fsq_id) REFERENCES businesses (fsq_id)
                )
            ''')
            
            # Create scan_history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scan_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    businesses_found INTEGER DEFAULT 0,
                    new_businesses INTEGER DEFAULT 0,
                    updated_businesses INTEGER DEFAULT 0,
                    scan_duration_seconds REAL DEFAULT 0.0,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    def initialize_database(self):
        """Public method to initialize database (for compatibility)."""
        self.init_db()
    
    # Business operations
    def save_business(self, business: Business) -> bool:
        """Save or update a business in the database."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO businesses (
                        fsq_id, name, categories, location_data, rating, hours_data,
                        website, phone, verified, popularity, first_seen, last_updated,
                        is_competitor, notes
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    business.fsq_id,
                    business.name,
                    json.dumps(business.categories),
                    json.dumps(business.location.to_dict()),
                    business.rating,
                    json.dumps(business.hours.to_dict()) if business.hours else None,
                    business.website,
                    business.phone,
                    business.verified,
                    business.popularity,
                    business.first_seen.isoformat() if business.first_seen else None,
                    business.last_updated.isoformat() if business.last_updated else None,
                    business.is_competitor,
                    business.notes
                ))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving business: {e}")
            return False
    
    def get_business(self, fsq_id: str) -> Optional[Business]:
        """Get a business by its Foursquare ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM businesses WHERE fsq_id = ?', (fsq_id,))
                row = cursor.fetchone()
                
                if row:
                    return self._row_to_business(row)
                return None
        except Exception as e:
            logger.error(f"Error getting business: {e}")
            return None
    
    def get_all_businesses(self, is_competitor: Optional[bool] = None) -> List[Business]:
        """Get all businesses, optionally filtered by competitor status."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if is_competitor is not None:
                    cursor.execute('SELECT * FROM businesses WHERE is_competitor = ?', (is_competitor,))
                else:
                    cursor.execute('SELECT * FROM businesses')
                
                rows = cursor.fetchall()
                return [self._row_to_business(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting businesses: {e}")
            return []
    
    def _row_to_business(self, row) -> Business:
        """Convert database row to Business object."""
        location_data = json.loads(row['location_data'])
        location = Location.from_dict(location_data)
        
        hours = None
        if row['hours_data']:
            hours_data = json.loads(row['hours_data'])
            hours = BusinessHours.from_dict(hours_data)
        
        return Business(
            fsq_id=row['fsq_id'],
            name=row['name'],
            categories=json.loads(row['categories']),
            location=location,
            rating=row['rating'],
            hours=hours,
            website=row['website'],
            phone=row['phone'],
            verified=bool(row['verified']),
            popularity=row['popularity'],
            first_seen=datetime.fromisoformat(row['first_seen']) if row['first_seen'] else None,
            last_updated=datetime.fromisoformat(row['last_updated']) if row['last_updated'] else None,
            is_competitor=bool(row['is_competitor']),
            notes=row['notes']
        )

    # Monitoring settings operations
    def save_monitoring_settings(self, settings: MonitoringSettings) -> int:
        """Save or update monitoring settings. Returns the ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if settings.id:
                    # Update existing
                    cursor.execute('''
                        UPDATE monitoring_settings SET
                            business_name = ?, business_location_lat = ?, business_location_lng = ?,
                            monitoring_radius = ?, scan_interval_minutes = ?, categories_to_monitor = ?,
                            exclude_categories = ?, min_rating_threshold = ?, notify_new_businesses = ?,
                            notify_rating_changes = ?, notify_trending = ?, status = ?, updated_at = ?
                        WHERE id = ?
                    ''', (
                        settings.business_name, settings.business_location_lat, settings.business_location_lng,
                        settings.monitoring_radius, settings.scan_interval_minutes,
                        json.dumps(settings.categories_to_monitor), json.dumps(settings.exclude_categories),
                        settings.min_rating_threshold, settings.notify_new_businesses,
                        settings.notify_rating_changes, settings.notify_trending, settings.status.value,
                        datetime.now().isoformat(), settings.id
                    ))
                    conn.commit()
                    return settings.id
                else:
                    # Insert new
                    cursor.execute('''
                        INSERT INTO monitoring_settings (
                            business_name, business_location_lat, business_location_lng,
                            monitoring_radius, scan_interval_minutes, categories_to_monitor,
                            exclude_categories, min_rating_threshold, notify_new_businesses,
                            notify_rating_changes, notify_trending, status
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        settings.business_name, settings.business_location_lat, settings.business_location_lng,
                        settings.monitoring_radius, settings.scan_interval_minutes,
                        json.dumps(settings.categories_to_monitor), json.dumps(settings.exclude_categories),
                        settings.min_rating_threshold, settings.notify_new_businesses,
                        settings.notify_rating_changes, settings.notify_trending, settings.status.value
                    ))
                    conn.commit()
                    return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving monitoring settings: {e}")
            return 0

    def get_monitoring_settings(self) -> Optional[MonitoringSettings]:
        """Get the current monitoring settings (assumes single configuration)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM monitoring_settings ORDER BY id DESC LIMIT 1')
                row = cursor.fetchone()

                if row:
                    return MonitoringSettings(
                        id=row['id'],
                        business_name=row['business_name'],
                        business_location_lat=row['business_location_lat'],
                        business_location_lng=row['business_location_lng'],
                        monitoring_radius=row['monitoring_radius'],
                        scan_interval_minutes=row['scan_interval_minutes'],
                        categories_to_monitor=json.loads(row['categories_to_monitor']) if row['categories_to_monitor'] else [],
                        exclude_categories=json.loads(row['exclude_categories']) if row['exclude_categories'] else [],
                        min_rating_threshold=row['min_rating_threshold'],
                        notify_new_businesses=bool(row['notify_new_businesses']),
                        notify_rating_changes=bool(row['notify_rating_changes']),
                        notify_trending=bool(row['notify_trending']),
                        status=MonitoringStatus(row['status']),
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        updated_at=datetime.fromisoformat(row['updated_at']) if row['updated_at'] else None
                    )
                return None
        except Exception as e:
            logger.error(f"Error getting monitoring settings: {e}")
            return None

    # Notification operations
    def save_notification(self, notification: Notification) -> int:
        """Save a notification. Returns the ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO notifications (
                        type, title, message, business_fsq_id, business_name, read, dismissed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    notification.type.value, notification.title, notification.message,
                    notification.business_fsq_id, notification.business_name,
                    notification.read, notification.dismissed
                ))

                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving notification: {e}")
            return 0

    def get_notifications(self, unread_only: bool = False, limit: int = 50) -> List[Notification]:
        """Get notifications, optionally filtered by read status."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                if unread_only:
                    cursor.execute('''
                        SELECT * FROM notifications WHERE read = FALSE AND dismissed = FALSE
                        ORDER BY created_at DESC LIMIT ?
                    ''', (limit,))
                else:
                    cursor.execute('''
                        SELECT * FROM notifications ORDER BY created_at DESC LIMIT ?
                    ''', (limit,))

                rows = cursor.fetchall()
                notifications = []

                for row in rows:
                    notification = Notification(
                        id=row['id'],
                        type=NotificationType(row['type']),
                        title=row['title'],
                        message=row['message'],
                        business_fsq_id=row['business_fsq_id'],
                        business_name=row['business_name'],
                        created_at=datetime.fromisoformat(row['created_at']) if row['created_at'] else None,
                        read=bool(row['read']),
                        dismissed=bool(row['dismissed'])
                    )
                    notifications.append(notification)

                return notifications
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []

    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE notifications SET read = TRUE WHERE id = ?', (notification_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return False

    def dismiss_notification(self, notification_id: int) -> bool:
        """Dismiss a notification."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('UPDATE notifications SET dismissed = TRUE WHERE id = ?', (notification_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error dismissing notification: {e}")
            return False

    # Scan history operations
    def save_scan_history(self, scan: ScanHistory) -> int:
        """Save scan history record. Returns the ID."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO scan_history (
                        businesses_found, new_businesses, updated_businesses,
                        scan_duration_seconds, success, error_message
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    scan.businesses_found, scan.new_businesses, scan.updated_businesses,
                    scan.scan_duration_seconds, scan.success, scan.error_message
                ))

                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving scan history: {e}")
            return 0

    def get_scan_history(self, limit: int = 20) -> List[ScanHistory]:
        """Get recent scan history."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM scan_history ORDER BY scan_timestamp DESC LIMIT ?
                ''', (limit,))

                rows = cursor.fetchall()
                scans = []

                for row in rows:
                    scan = ScanHistory(
                        id=row['id'],
                        scan_timestamp=datetime.fromisoformat(row['scan_timestamp']) if row['scan_timestamp'] else None,
                        businesses_found=row['businesses_found'],
                        new_businesses=row['new_businesses'],
                        updated_businesses=row['updated_businesses'],
                        scan_duration_seconds=row['scan_duration_seconds'],
                        success=bool(row['success']),
                        error_message=row['error_message']
                    )
                    scans.append(scan)

                return scans
        except Exception as e:
            logger.error(f"Error getting scan history: {e}")
            return []

    def get_businesses_within_radius(self, lat: float, lng: float, radius_km: float) -> List[Business]:
        """Get businesses within a specified radius (simplified - uses bounding box)."""
        try:
            # Simple bounding box calculation (not perfect for large distances)
            lat_delta = radius_km / 111.0  # Approximate km per degree latitude
            lng_delta = radius_km / (111.0 * abs(lat))  # Approximate km per degree longitude

            min_lat = lat - lat_delta
            max_lat = lat + lat_delta
            min_lng = lng - lng_delta
            max_lng = lng + lng_delta

            businesses = self.get_all_businesses()
            filtered_businesses = []

            for business in businesses:
                if (min_lat <= business.location.latitude <= max_lat and
                    min_lng <= business.location.longitude <= max_lng):
                    # For more accurate distance, we could use the distance_from method
                    filtered_businesses.append(business)

            return filtered_businesses
        except Exception as e:
            logger.error(f"Error getting businesses within radius: {e}")
            return []
