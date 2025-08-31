"""
Monitoring configuration and notification models for BizRadar application.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum

class NotificationType(Enum):
    """Types of notifications that can be sent."""
    NEW_BUSINESS = "new_business"
    BUSINESS_UPDATED = "business_updated"
    TRENDING_ACTIVITY = "trending_activity"
    RATING_CHANGE = "rating_change"
    COMPETITOR_ALERT = "competitor_alert"

class MonitoringStatus(Enum):
    """Status of monitoring configuration."""
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"

@dataclass
class MonitoringSettings:
    """Configuration for business monitoring."""
    id: Optional[int] = None
    business_name: str = ""
    business_location_lat: float = 0.0
    business_location_lng: float = 0.0
    monitoring_radius: int = 1000  # meters
    scan_interval_minutes: int = 60
    categories_to_monitor: List[str] = None
    exclude_categories: List[str] = None
    min_rating_threshold: Optional[float] = None
    notify_new_businesses: bool = True
    notify_rating_changes: bool = True
    notify_trending: bool = True
    status: MonitoringStatus = MonitoringStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.categories_to_monitor is None:
            self.categories_to_monitor = []
        if self.exclude_categories is None:
            self.exclude_categories = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        # Convert enums to strings
        data['status'] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MonitoringSettings':
        # Convert ISO strings back to datetime objects
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if 'updated_at' in data and data['updated_at']:
            data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # Convert string to enum
        if 'status' in data and isinstance(data['status'], str):
            data['status'] = MonitoringStatus(data['status'])
        
        return cls(**data)

@dataclass
class Notification:
    """Notification data model."""
    id: Optional[int] = None
    type: NotificationType = NotificationType.NEW_BUSINESS
    title: str = ""
    message: str = ""
    business_fsq_id: Optional[str] = None
    business_name: Optional[str] = None
    created_at: Optional[datetime] = None
    read: bool = False
    dismissed: bool = False
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        # Convert datetime objects to ISO strings
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        # Convert enum to string
        data['type'] = self.type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Notification':
        # Convert ISO string back to datetime object
        if 'created_at' in data and data['created_at']:
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        
        # Convert string to enum
        if 'type' in data and isinstance(data['type'], str):
            data['type'] = NotificationType(data['type'])
        
        return cls(**data)

@dataclass
class ScanHistory:
    """History of monitoring scans."""
    id: Optional[int] = None
    scan_timestamp: Optional[datetime] = None
    businesses_found: int = 0
    new_businesses: int = 0
    updated_businesses: int = 0
    scan_duration_seconds: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.scan_timestamp is None:
            self.scan_timestamp = datetime.now()
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        # Convert datetime object to ISO string
        if self.scan_timestamp:
            data['scan_timestamp'] = self.scan_timestamp.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ScanHistory':
        # Convert ISO string back to datetime object
        if 'scan_timestamp' in data and data['scan_timestamp']:
            data['scan_timestamp'] = datetime.fromisoformat(data['scan_timestamp'])
        
        return cls(**data)
