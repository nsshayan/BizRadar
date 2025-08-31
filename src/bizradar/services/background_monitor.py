"""
Background monitoring service for BizRadar application.

Handles automated periodic scanning for business changes using a separate thread.
"""

import threading
import time
import logging
import schedule
from datetime import datetime
from typing import Optional

from ..api.foursquare_client import FoursquareClient
from ..services.monitoring_service import MonitoringService
from ..services.notification_service import NotificationService
from ..utils.database import DatabaseManager
from ..models.monitoring import MonitoringSettings, MonitoringStatus

logger = logging.getLogger(__name__)

class BackgroundMonitor:
    """Background service for automated business monitoring."""
    
    def __init__(self, foursquare_client: FoursquareClient, db_manager: DatabaseManager, 
                 notification_service: NotificationService):
        self.foursquare_client = foursquare_client
        self.db_manager = db_manager
        self.notification_service = notification_service
        self.monitoring_service = MonitoringService(foursquare_client, db_manager)
        
        # Threading control
        self.monitor_thread = None
        self.stop_event = threading.Event()
        self.is_running = False
        
        # Current settings
        self.current_settings = None
        
        # Schedule management
        self.scheduler_running = False
    
    def start(self):
        """Start the background monitoring service."""
        if self.is_running:
            logger.warning("Background monitor is already running")
            return False
        
        try:
            # Load current settings
            self.current_settings = self.db_manager.get_monitoring_settings()
            if not self.current_settings:
                logger.error("No monitoring settings found - cannot start background monitor")
                return False
            
            if self.current_settings.status != MonitoringStatus.ACTIVE:
                logger.info("Monitoring is not active - background monitor will not start")
                return False
            
            # Clear any existing scheduled jobs
            schedule.clear()
            
            # Schedule the monitoring job
            interval = self.current_settings.scan_interval_minutes
            schedule.every(interval).minutes.do(self.run_scheduled_scan)
            
            # Start the monitoring thread
            self.stop_event.clear()
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            self.is_running = True
            logger.info(f"Background monitor started with {interval} minute intervals")
            
            # Send notification about monitoring start
            from ..models.monitoring import NotificationType
            self.notification_service.create_notification(
                notification_type=NotificationType.COMPETITOR_ALERT,
                title="Monitoring Started",
                message=f"Background monitoring started for {self.current_settings.business_name}",
                send_desktop=True
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start background monitor: {e}")
            return False
    
    def stop(self):
        """Stop the background monitoring service."""
        if not self.is_running:
            logger.warning("Background monitor is not running")
            return
        
        try:
            # Signal the thread to stop
            self.stop_event.set()
            
            # Clear scheduled jobs
            schedule.clear()
            
            # Wait for thread to finish (with timeout)
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=5.0)
            
            self.is_running = False
            self.scheduler_running = False
            
            logger.info("Background monitor stopped")
            
            # Send notification about monitoring stop
            from ..models.monitoring import NotificationType
            self.notification_service.create_notification(
                notification_type=NotificationType.COMPETITOR_ALERT,
                title="Monitoring Stopped",
                message="Background monitoring has been stopped",
                send_desktop=True
            )
            
        except Exception as e:
            logger.error(f"Error stopping background monitor: {e}")
    
    def restart(self):
        """Restart the background monitoring service."""
        logger.info("Restarting background monitor")
        self.stop()
        time.sleep(1)  # Brief pause
        return self.start()
    
    def update_settings(self, new_settings: MonitoringSettings):
        """Update monitoring settings and restart if necessary."""
        old_interval = self.current_settings.scan_interval_minutes if self.current_settings else 0
        old_status = self.current_settings.status if self.current_settings else MonitoringStatus.INACTIVE
        
        self.current_settings = new_settings
        
        # Check if we need to restart due to interval change
        if (self.is_running and 
            (new_settings.scan_interval_minutes != old_interval or 
             new_settings.status != old_status)):
            
            if new_settings.status == MonitoringStatus.ACTIVE:
                logger.info("Settings changed - restarting background monitor")
                self.restart()
            else:
                logger.info("Monitoring disabled - stopping background monitor")
                self.stop()
    
    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        logger.info("Background monitor loop started")
        self.scheduler_running = True
        
        try:
            while not self.stop_event.is_set():
                # Run pending scheduled jobs
                schedule.run_pending()
                
                # Sleep for a short interval
                time.sleep(10)  # Check every 10 seconds
                
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
        finally:
            self.scheduler_running = False
            logger.info("Background monitor loop ended")
    
    def run_scheduled_scan(self):
        """Run a scheduled monitoring scan."""
        try:
            logger.info("Running scheduled monitoring scan")
            
            # Reload settings in case they changed
            current_settings = self.db_manager.get_monitoring_settings()
            if not current_settings or current_settings.status != MonitoringStatus.ACTIVE:
                logger.info("Monitoring is no longer active - skipping scan")
                return
            
            # Perform the scan
            scan_result = self.monitoring_service.perform_scan(current_settings)
            
            if scan_result.success:
                logger.info(f"Scheduled scan completed: {scan_result.new_businesses} new, "
                           f"{scan_result.updated_businesses} updated businesses")
                
                # Send summary notification if there were significant changes
                if scan_result.new_businesses > 0 or scan_result.updated_businesses > 5:
                    from ..models.monitoring import NotificationType
                    self.notification_service.create_notification(
                        notification_type=NotificationType.COMPETITOR_ALERT,
                        title="Scan Summary",
                        message=f"Scan found {scan_result.new_businesses} new and "
                               f"{scan_result.updated_businesses} updated businesses",
                        send_desktop=True
                    )
            else:
                logger.error(f"Scheduled scan failed: {scan_result.error_message}")
                
                # Send error notification
                from ..models.monitoring import NotificationType
                self.notification_service.create_notification(
                    notification_type=NotificationType.COMPETITOR_ALERT,
                    title="Scan Failed",
                    message=f"Scheduled scan failed: {scan_result.error_message}",
                    send_desktop=True
                )
                
        except Exception as e:
            logger.error(f"Error in scheduled scan: {e}")
            
            # Send error notification
            from ..models.monitoring import NotificationType
            self.notification_service.create_notification(
                notification_type=NotificationType.COMPETITOR_ALERT,
                title="Scan Error",
                message=f"Error during scheduled scan: {str(e)}",
                send_desktop=True
            )
    
    def run_manual_scan(self) -> bool:
        """Run a manual scan immediately."""
        try:
            if not self.current_settings:
                self.current_settings = self.db_manager.get_monitoring_settings()
                if not self.current_settings:
                    logger.error("No monitoring settings available for manual scan")
                    return False
            
            logger.info("Running manual monitoring scan")
            scan_result = self.monitoring_service.perform_scan(self.current_settings)
            
            if scan_result.success:
                logger.info(f"Manual scan completed: {scan_result.new_businesses} new, "
                           f"{scan_result.updated_businesses} updated businesses")
                return True
            else:
                logger.error(f"Manual scan failed: {scan_result.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Error in manual scan: {e}")
            return False
    
    def get_status(self) -> dict:
        """Get the current status of the background monitor."""
        return {
            'is_running': self.is_running,
            'scheduler_running': self.scheduler_running,
            'settings_loaded': self.current_settings is not None,
            'monitoring_status': self.current_settings.status.value if self.current_settings else 'unknown',
            'scan_interval': self.current_settings.scan_interval_minutes if self.current_settings else 0,
            'business_name': self.current_settings.business_name if self.current_settings else 'Unknown',
            'next_scan': self.get_next_scan_time()
        }
    
    def get_next_scan_time(self) -> Optional[str]:
        """Get the time of the next scheduled scan."""
        try:
            if schedule.jobs:
                next_run = schedule.next_run()
                if next_run:
                    return next_run.strftime('%Y-%m-%d %H:%M:%S')
            return None
        except Exception:
            return None
    
    def force_scan_now(self):
        """Force an immediate scan (bypassing the schedule)."""
        if self.current_settings and self.current_settings.status == MonitoringStatus.ACTIVE:
            # Run scan in a separate thread to avoid blocking
            scan_thread = threading.Thread(target=self.run_scheduled_scan, daemon=True)
            scan_thread.start()
            return True
        return False
