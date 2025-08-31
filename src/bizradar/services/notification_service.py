"""
Notification service for BizRadar application.

Handles system notifications and alerts for business monitoring events.
"""

import logging
from typing import List, Optional
from datetime import datetime, timedelta

try:
    from plyer import notification as plyer_notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False
    logging.warning("Plyer not available - desktop notifications will be disabled")

from ..models.monitoring import Notification, NotificationType
from ..utils.database import DatabaseManager

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing and sending notifications."""
    
    def __init__(self, db_manager: DatabaseManager, enable_desktop_notifications: bool = True):
        self.db_manager = db_manager
        self.enable_desktop_notifications = enable_desktop_notifications and PLYER_AVAILABLE
    
    def send_desktop_notification(self, title: str, message: str, timeout: int = 10):
        """Send a desktop notification using plyer."""
        if not self.enable_desktop_notifications:
            return
        
        try:
            plyer_notification.notify(
                title=title,
                message=message,
                app_name="BizRadar",
                timeout=timeout
            )
            logger.info(f"Desktop notification sent: {title}")
        except Exception as e:
            logger.error(f"Failed to send desktop notification: {e}")
    
    def create_notification(self, notification_type: NotificationType, title: str, 
                          message: str, business_fsq_id: Optional[str] = None,
                          business_name: Optional[str] = None, 
                          send_desktop: bool = True) -> int:
        """Create and save a notification, optionally sending desktop notification."""
        notification = Notification(
            type=notification_type,
            title=title,
            message=message,
            business_fsq_id=business_fsq_id,
            business_name=business_name
        )
        
        notification_id = self.db_manager.save_notification(notification)
        
        if send_desktop and notification_id:
            self.send_desktop_notification(title, message)
        
        return notification_id
    
    def get_unread_notifications(self) -> List[Notification]:
        """Get all unread notifications."""
        return self.db_manager.get_notifications(unread_only=True)
    
    def get_recent_notifications(self, hours: int = 24, limit: int = 50) -> List[Notification]:
        """Get notifications from the last N hours."""
        all_notifications = self.db_manager.get_notifications(limit=limit)
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [n for n in all_notifications if n.created_at and n.created_at >= cutoff_time]
    
    def mark_notification_read(self, notification_id: int) -> bool:
        """Mark a notification as read."""
        return self.db_manager.mark_notification_read(notification_id)
    
    def dismiss_notification(self, notification_id: int) -> bool:
        """Dismiss a notification."""
        return self.db_manager.dismiss_notification(notification_id)
    
    def mark_all_read(self) -> int:
        """Mark all unread notifications as read. Returns count of notifications marked."""
        unread_notifications = self.get_unread_notifications()
        count = 0
        
        for notification in unread_notifications:
            if self.mark_notification_read(notification.id):
                count += 1
        
        return count
    
    def get_notification_summary(self) -> dict:
        """Get a summary of notification statistics."""
        try:
            all_notifications = self.db_manager.get_notifications(limit=100)
            unread_count = len([n for n in all_notifications if not n.read and not n.dismissed])
            
            # Count by type
            type_counts = {}
            for notification in all_notifications:
                type_name = notification.type.value
                type_counts[type_name] = type_counts.get(type_name, 0) + 1
            
            # Recent activity (last 24 hours)
            recent_notifications = self.get_recent_notifications(hours=24)
            recent_count = len(recent_notifications)
            
            return {
                'total_notifications': len(all_notifications),
                'unread_count': unread_count,
                'recent_count': recent_count,
                'type_breakdown': type_counts
            }
        except Exception as e:
            logger.error(f"Error getting notification summary: {e}")
            return {
                'total_notifications': 0,
                'unread_count': 0,
                'recent_count': 0,
                'type_breakdown': {}
            }
    
    def create_competitor_alert(self, business_name: str, business_fsq_id: str, 
                              alert_type: str = "new") -> int:
        """Create a competitor-specific alert notification."""
        if alert_type == "new":
            title = "New Competitor Alert"
            message = f"A new competitor '{business_name}' has been detected in your monitoring area."
            notification_type = NotificationType.NEW_BUSINESS
        elif alert_type == "updated":
            title = "Competitor Update"
            message = f"Competitor '{business_name}' has updated their information."
            notification_type = NotificationType.BUSINESS_UPDATED
        elif alert_type == "trending":
            title = "Trending Competitor"
            message = f"'{business_name}' is showing increased activity and trending in your area."
            notification_type = NotificationType.TRENDING_ACTIVITY
        else:
            title = "Competitor Alert"
            message = f"Activity detected for competitor '{business_name}'."
            notification_type = NotificationType.COMPETITOR_ALERT
        
        return self.create_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            business_fsq_id=business_fsq_id,
            business_name=business_name
        )
    
    def create_rating_change_alert(self, business_name: str, business_fsq_id: str,
                                 old_rating: Optional[float], new_rating: Optional[float]) -> int:
        """Create a notification for rating changes."""
        if old_rating is None and new_rating is not None:
            message = f"'{business_name}' now has a rating of {new_rating:.1f} stars."
        elif old_rating is not None and new_rating is None:
            message = f"'{business_name}' no longer has a visible rating."
        elif old_rating is not None and new_rating is not None:
            change = new_rating - old_rating
            direction = "increased" if change > 0 else "decreased"
            message = f"'{business_name}' rating {direction} from {old_rating:.1f} to {new_rating:.1f} stars."
        else:
            message = f"Rating information updated for '{business_name}'."
        
        return self.create_notification(
            notification_type=NotificationType.RATING_CHANGE,
            title="Rating Change Alert",
            message=message,
            business_fsq_id=business_fsq_id,
            business_name=business_name
        )
