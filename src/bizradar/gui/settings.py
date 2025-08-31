"""
Settings view for BizRadar application.

Contains the settings interface for configuring monitoring preferences and API settings.
"""

import flet as ft
from typing import List

from ..models.monitoring import MonitoringSettings, MonitoringStatus

class SettingsView:
    """Settings view component."""
    
    def __init__(self, app):
        self.app = app
        self.settings = None
        
        # UI components
        self.business_name_field = None
        self.latitude_field = None
        self.longitude_field = None
        self.radius_slider = None
        self.interval_dropdown = None
        self.categories_field = None
        self.exclude_categories_field = None
        self.min_rating_slider = None
        self.notify_new_checkbox = None
        self.notify_rating_checkbox = None
        self.notify_trending_checkbox = None
        self.status_dropdown = None
        self.api_key_field = None
    
    def build(self) -> ft.Control:
        """Build the settings interface."""
        self.load_settings()
        
        # API Configuration Section
        api_section = self.create_api_section()
        
        # Business Location Section
        location_section = self.create_location_section()
        
        # Monitoring Configuration Section
        monitoring_section = self.create_monitoring_section()
        
        # Notification Settings Section
        notification_section = self.create_notification_section()
        
        # Action buttons
        action_buttons = ft.Row([
            ft.ElevatedButton(
                text="Save Settings",
                icon=ft.Icons.SAVE,
                on_click=self.save_settings,
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            ),
            ft.OutlinedButton(
                text="Reset to Defaults",
                icon=ft.Icons.RESTORE,
                on_click=self.reset_settings
            ),
            ft.OutlinedButton(
                text="Test Connection",
                icon=ft.Icons.WIFI,
                on_click=self.test_api_connection
            )
        ], spacing=10)
        
        # Main settings layout
        settings_layout = ft.Column([
            ft.Text("Settings", size=24, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            api_section,
            ft.Divider(),
            location_section,
            ft.Divider(),
            monitoring_section,
            ft.Divider(),
            notification_section,
            ft.Divider(),
            action_buttons
        ], spacing=20, scroll=ft.ScrollMode.AUTO)
        
        return ft.Container(
            content=settings_layout,
            padding=20,
            expand=True
        )
    
    def load_settings(self):
        """Load current settings from database."""
        self.settings = self.app.db_manager.get_monitoring_settings()
        if not self.settings:
            # Create default settings
            self.settings = MonitoringSettings()
    
    def create_api_section(self) -> ft.Container:
        """Create API configuration section."""
        self.api_key_field = ft.TextField(
            label="Foursquare API Key",
            value=self.app.config.foursquare_api_key,
            password=True,
            hint_text="Enter your Foursquare Places API key",
            width=400
        )
        
        api_help = ft.Text(
            "Get your API key from https://developer.foursquare.com/",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("API Configuration", size=18, weight=ft.FontWeight.BOLD),
                self.api_key_field,
                api_help
            ], spacing=10),
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8
        )
    
    def create_location_section(self) -> ft.Container:
        """Create business location configuration section."""
        self.business_name_field = ft.TextField(
            label="Your Business Name",
            value=self.settings.business_name,
            hint_text="Enter your business name",
            width=300
        )
        
        self.latitude_field = ft.TextField(
            label="Latitude",
            value=str(self.settings.business_location_lat) if self.settings.business_location_lat else "",
            hint_text="e.g., 40.7128",
            width=150
        )
        
        self.longitude_field = ft.TextField(
            label="Longitude",
            value=str(self.settings.business_location_lng) if self.settings.business_location_lng else "",
            hint_text="e.g., -74.0060",
            width=150
        )
        
        location_help = ft.Text(
            "You can get coordinates from Google Maps by right-clicking on your location",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Business Location", size=18, weight=ft.FontWeight.BOLD),
                self.business_name_field,
                ft.Row([self.latitude_field, self.longitude_field], spacing=10),
                location_help
            ], spacing=10),
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8
        )
    
    def create_monitoring_section(self) -> ft.Container:
        """Create monitoring configuration section."""
        self.radius_slider = ft.Slider(
            min=100,
            max=5000,
            divisions=49,
            value=self.settings.monitoring_radius,
            label="Radius: {value}m",
            width=300
        )
        
        self.interval_dropdown = ft.Dropdown(
            label="Scan Interval",
            options=[
                ft.dropdown.Option("15", "15 minutes"),
                ft.dropdown.Option("30", "30 minutes"),
                ft.dropdown.Option("60", "1 hour"),
                ft.dropdown.Option("120", "2 hours"),
                ft.dropdown.Option("240", "4 hours"),
                ft.dropdown.Option("480", "8 hours"),
                ft.dropdown.Option("1440", "24 hours")
            ],
            value=str(self.settings.scan_interval_minutes),
            width=200
        )
        
        self.categories_field = ft.TextField(
            label="Categories to Monitor (comma-separated)",
            value=", ".join(self.settings.categories_to_monitor) if self.settings.categories_to_monitor else "",
            hint_text="e.g., Restaurant, Retail, Coffee Shop",
            width=400,
            multiline=True,
            max_lines=3
        )
        
        self.exclude_categories_field = ft.TextField(
            label="Categories to Exclude (comma-separated)",
            value=", ".join(self.settings.exclude_categories) if self.settings.exclude_categories else "",
            hint_text="e.g., Gas Station, ATM",
            width=400,
            multiline=True,
            max_lines=3
        )
        
        self.min_rating_slider = ft.Slider(
            min=0,
            max=5,
            divisions=10,
            value=self.settings.min_rating_threshold or 0,
            label="Min Rating: {value}",
            width=200
        )
        
        self.status_dropdown = ft.Dropdown(
            label="Monitoring Status",
            options=[
                ft.dropdown.Option("active", "Active"),
                ft.dropdown.Option("paused", "Paused"),
                ft.dropdown.Option("inactive", "Inactive")
            ],
            value=self.settings.status.value,
            width=150
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Monitoring Configuration", size=18, weight=ft.FontWeight.BOLD),
                ft.Row([
                    ft.Column([ft.Text("Monitoring Radius"), self.radius_slider]),
                    self.interval_dropdown,
                    self.status_dropdown
                ], spacing=20),
                self.categories_field,
                self.exclude_categories_field,
                ft.Row([
                    ft.Column([ft.Text("Minimum Rating Filter"), self.min_rating_slider])
                ])
            ], spacing=15),
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8
        )
    
    def create_notification_section(self) -> ft.Container:
        """Create notification settings section."""
        self.notify_new_checkbox = ft.Checkbox(
            label="Notify about new businesses",
            value=self.settings.notify_new_businesses
        )
        
        self.notify_rating_checkbox = ft.Checkbox(
            label="Notify about rating changes",
            value=self.settings.notify_rating_changes
        )
        
        self.notify_trending_checkbox = ft.Checkbox(
            label="Notify about trending activity",
            value=self.settings.notify_trending
        )
        
        return ft.Container(
            content=ft.Column([
                ft.Text("Notification Settings", size=18, weight=ft.FontWeight.BOLD),
                self.notify_new_checkbox,
                self.notify_rating_checkbox,
                self.notify_trending_checkbox
            ], spacing=10),
            padding=15,
            bgcolor=ft.Colors.GREY_50,
            border_radius=8
        )
    
    def save_settings(self, e):
        """Save the current settings."""
        try:
            # Update API key if changed
            if self.api_key_field.value != self.app.config.foursquare_api_key:
                if self.app.config.update_api_key(self.api_key_field.value):
                    # Reinitialize services
                    from ..api.foursquare_client import FoursquareClient
                    from ..services.monitoring_service import MonitoringService
                    
                    self.app.foursquare_client = FoursquareClient(self.api_key_field.value)
                    self.app.monitoring_service = MonitoringService(self.app.foursquare_client, self.app.db_manager)
                else:
                    self.app.show_error_message("Failed to save API key")
                    return
            
            # Update monitoring settings
            self.settings.business_name = self.business_name_field.value
            self.settings.business_location_lat = float(self.latitude_field.value) if self.latitude_field.value else 0.0
            self.settings.business_location_lng = float(self.longitude_field.value) if self.longitude_field.value else 0.0
            self.settings.monitoring_radius = int(self.radius_slider.value)
            self.settings.scan_interval_minutes = int(self.interval_dropdown.value)
            
            # Parse categories
            if self.categories_field.value:
                self.settings.categories_to_monitor = [cat.strip() for cat in self.categories_field.value.split(",")]
            else:
                self.settings.categories_to_monitor = []
            
            if self.exclude_categories_field.value:
                self.settings.exclude_categories = [cat.strip() for cat in self.exclude_categories_field.value.split(",")]
            else:
                self.settings.exclude_categories = []
            
            self.settings.min_rating_threshold = self.min_rating_slider.value if self.min_rating_slider.value > 0 else None
            self.settings.notify_new_businesses = self.notify_new_checkbox.value
            self.settings.notify_rating_changes = self.notify_rating_checkbox.value
            self.settings.notify_trending = self.notify_trending_checkbox.value
            self.settings.status = MonitoringStatus(self.status_dropdown.value)
            
            # Save to database
            settings_id = self.app.db_manager.save_monitoring_settings(self.settings)
            if settings_id:
                self.app.show_success_message("Settings saved successfully!")
            else:
                self.app.show_error_message("Failed to save settings")
                
        except ValueError as ve:
            self.app.show_error_message(f"Invalid input: {str(ve)}")
        except Exception as ex:
            self.app.show_error_message(f"Error saving settings: {str(ex)}")
    
    def reset_settings(self, e):
        """Reset settings to defaults."""
        self.settings = MonitoringSettings()
        self.refresh()
        self.app.show_info_message("Settings reset to defaults")
    
    def test_api_connection(self, e):
        """Test the API connection."""
        if not self.app.foursquare_client:
            self.app.show_error_message("Please save your API key first")
            return
        
        try:
            # Test with a simple search
            places = self.app.foursquare_client.search_nearby(40.7128, -74.0060, 1000, limit=1)
            if places:
                self.app.show_success_message("API connection successful!")
            else:
                self.app.show_error_message("API connection failed - no results returned")
        except Exception as ex:
            self.app.show_error_message(f"API connection failed: {str(ex)}")
    
    def refresh(self):
        """Refresh the settings view."""
        self.load_settings()
        # Update UI components with new values
        if self.business_name_field:
            self.business_name_field.value = self.settings.business_name
        if self.latitude_field:
            self.latitude_field.value = str(self.settings.business_location_lat) if self.settings.business_location_lat else ""
        # ... update other fields
        self.app.page.update()
