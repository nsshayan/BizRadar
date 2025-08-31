"""
Monitoring service for BizRadar application.

Handles competitor monitoring logic, change detection, and notification triggers.
"""

import logging
import time
from datetime import datetime
from typing import List, Optional, Tuple, Set
from geopy.distance import geodesic

from ..api.foursquare_client import FoursquareClient, PlaceData
from ..models.business import Business, Location
from ..models.monitoring import MonitoringSettings, Notification, ScanHistory, NotificationType
from ..utils.database import DatabaseManager

logger = logging.getLogger(__name__)

class MonitoringService:
    """Service for monitoring competitor businesses and detecting changes."""
    
    def __init__(self, foursquare_client: FoursquareClient, db_manager: DatabaseManager):
        self.foursquare_client = foursquare_client
        self.db_manager = db_manager
    
    def perform_scan(self, settings: MonitoringSettings) -> ScanHistory:
        """Perform a complete monitoring scan based on settings."""
        start_time = time.time()
        scan_result = ScanHistory()
        
        try:
            logger.info(f"Starting monitoring scan for {settings.business_name}")
            
            # Get places from Foursquare API
            places = self.foursquare_client.search_nearby(
                latitude=settings.business_location_lat,
                longitude=settings.business_location_lng,
                radius=settings.monitoring_radius,
                categories=settings.categories_to_monitor if settings.categories_to_monitor else None,
                limit=50
            )
            
            scan_result.businesses_found = len(places)
            
            # Process each place
            new_businesses = []
            updated_businesses = []
            
            for place in places:
                # Skip if in exclude categories
                if self._should_exclude_business(place, settings):
                    continue
                
                # Check if business already exists
                existing_business = self.db_manager.get_business(place.fsq_id)
                
                if existing_business:
                    # Check for updates
                    if self._update_existing_business(existing_business, place, settings):
                        updated_businesses.append(existing_business)
                        self.db_manager.save_business(existing_business)
                else:
                    # New business found
                    new_business = self._create_business_from_place(place, settings)
                    if new_business:
                        new_businesses.append(new_business)
                        self.db_manager.save_business(new_business)
            
            scan_result.new_businesses = len(new_businesses)
            scan_result.updated_businesses = len(updated_businesses)
            
            # Generate notifications
            self._generate_notifications(new_businesses, updated_businesses, settings)
            
            scan_result.success = True
            logger.info(f"Scan completed: {scan_result.new_businesses} new, {scan_result.updated_businesses} updated")
            
        except Exception as e:
            scan_result.success = False
            scan_result.error_message = str(e)
            logger.error(f"Scan failed: {e}")
        
        finally:
            scan_result.scan_duration_seconds = time.time() - start_time
            self.db_manager.save_scan_history(scan_result)
        
        return scan_result
    
    def _should_exclude_business(self, place: PlaceData, settings: MonitoringSettings) -> bool:
        """Check if a business should be excluded based on settings."""
        # Check exclude categories
        if settings.exclude_categories:
            for category in place.categories:
                if any(excluded.lower() in category.lower() for excluded in settings.exclude_categories):
                    return True
        
        # Check minimum rating threshold
        if settings.min_rating_threshold and place.rating:
            if place.rating < settings.min_rating_threshold:
                return True
        
        return False
    
    def _update_existing_business(self, business: Business, place: PlaceData, settings: MonitoringSettings) -> bool:
        """Update existing business with new data. Returns True if changes were made."""
        return business.update_from_api_data(place)
    
    def _create_business_from_place(self, place: PlaceData, settings: MonitoringSettings) -> Optional[Business]:
        """Create a new Business object from PlaceData."""
        try:
            location = Location(
                latitude=place.location.get('latitude', 0),
                longitude=place.location.get('longitude', 0),
                address=place.location.get('address'),
                city=place.location.get('locality'),
                state=place.location.get('region'),
                postal_code=place.location.get('postcode'),
                country=place.location.get('country')
            )
            
            business = Business(
                fsq_id=place.fsq_id,
                name=place.name,
                categories=place.categories,
                location=location,
                rating=place.rating,
                website=place.website,
                phone=place.tel,
                verified=place.verified,
                popularity=place.popularity,
                is_competitor=self._is_potential_competitor(place, settings)
            )
            
            return business
        except Exception as e:
            logger.error(f"Error creating business from place data: {e}")
            return None
    
    def _is_potential_competitor(self, place: PlaceData, settings: MonitoringSettings) -> bool:
        """Determine if a business is a potential competitor."""
        # Simple heuristic: if categories match monitoring categories, it's a competitor
        if settings.categories_to_monitor:
            for category in place.categories:
                if any(monitored.lower() in category.lower() for monitored in settings.categories_to_monitor):
                    return True
        
        # If no specific categories are being monitored, consider all as potential competitors
        return not settings.categories_to_monitor
    
    def _generate_notifications(self, new_businesses: List[Business], updated_businesses: List[Business], 
                              settings: MonitoringSettings):
        """Generate notifications based on scan results."""
        # Notifications for new businesses
        if settings.notify_new_businesses and new_businesses:
            for business in new_businesses:
                if business.is_competitor:
                    notification = Notification(
                        type=NotificationType.NEW_BUSINESS,
                        title="New Competitor Detected",
                        message=f"A new business '{business.name}' has opened nearby in the {', '.join(business.categories)} category.",
                        business_fsq_id=business.fsq_id,
                        business_name=business.name
                    )
                    self.db_manager.save_notification(notification)
        
        # Notifications for updated businesses
        if settings.notify_rating_changes and updated_businesses:
            for business in updated_businesses:
                # This is a simplified check - in a real implementation, you'd track specific changes
                notification = Notification(
                    type=NotificationType.BUSINESS_UPDATED,
                    title="Competitor Updated",
                    message=f"'{business.name}' has updated information. Current rating: {business.rating or 'N/A'}",
                    business_fsq_id=business.fsq_id,
                    business_name=business.name
                )
                self.db_manager.save_notification(notification)
    
    def get_trending_businesses(self, settings: MonitoringSettings) -> List[Business]:
        """Get businesses with trending activity in the monitoring area."""
        try:
            trending_places = self.foursquare_client.get_trending_places(
                latitude=settings.business_location_lat,
                longitude=settings.business_location_lng,
                radius=settings.monitoring_radius
            )
            
            trending_businesses = []
            for place in trending_places:
                business = self.db_manager.get_business(place.fsq_id)
                if business:
                    trending_businesses.append(business)
                else:
                    # Create new business if not in database
                    new_business = self._create_business_from_place(place, settings)
                    if new_business:
                        self.db_manager.save_business(new_business)
                        trending_businesses.append(new_business)
            
            return trending_businesses
        except Exception as e:
            logger.error(f"Error getting trending businesses: {e}")
            return []
    
    def get_competitors_summary(self, settings: MonitoringSettings) -> dict:
        """Get a summary of competitors in the monitoring area."""
        try:
            # Get all businesses within radius
            businesses = self.db_manager.get_businesses_within_radius(
                settings.business_location_lat,
                settings.business_location_lng,
                settings.monitoring_radius / 1000  # Convert to km
            )
            
            competitors = [b for b in businesses if b.is_competitor]
            
            # Calculate statistics
            total_competitors = len(competitors)
            avg_rating = sum(c.rating for c in competitors if c.rating) / max(len([c for c in competitors if c.rating]), 1)
            verified_count = len([c for c in competitors if c.verified])
            
            # Group by categories
            category_counts = {}
            for competitor in competitors:
                for category in competitor.categories:
                    category_counts[category] = category_counts.get(category, 0) + 1
            
            return {
                'total_competitors': total_competitors,
                'average_rating': round(avg_rating, 2) if avg_rating else 0,
                'verified_businesses': verified_count,
                'category_breakdown': category_counts,
                'recent_additions': len([c for c in competitors if c.first_seen and 
                                       (datetime.now() - c.first_seen).days <= 30])
            }
        except Exception as e:
            logger.error(f"Error getting competitors summary: {e}")
            return {
                'total_competitors': 0,
                'average_rating': 0,
                'verified_businesses': 0,
                'category_breakdown': {},
                'recent_additions': 0
            }
