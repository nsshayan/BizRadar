"""
Main application interface for BizRadar.

Contains the primary Flet application class and navigation structure.
"""

import flet as ft
import logging
from typing import Optional

from ..api.foursquare_client import FoursquareClient
from ..services.monitoring_service import MonitoringService
from ..services.notification_service import NotificationService
from ..utils.config import Config
from ..utils.database import DatabaseManager
from .dashboard import DashboardView
from .settings import SettingsView
from .notifications import NotificationsView

logger = logging.getLogger(__name__)

class BizRadarApp:
    """Main BizRadar application class."""
    
    def __init__(self, page: ft.Page, config: Config, db_manager: DatabaseManager):
        self.page = page
        self.config = config
        self.db_manager = db_manager
        
        # Initialize services
        self.foursquare_client = None
        self.monitoring_service = None
        self.notification_service = NotificationService(db_manager, config.enable_notifications)
        
        # Initialize API client if configured
        if config.is_configured():
            self.foursquare_client = FoursquareClient(config.foursquare_api_key)
            self.monitoring_service = MonitoringService(self.foursquare_client, db_manager)
        
        # Initialize views
        self.dashboard_view = None
        self.settings_view = None
        self.notifications_view = None
        
        # Current view tracking
        self.current_view = "dashboard"
        
        # Setup page
        self.setup_page()
    
    def setup_page(self):
        """Configure the main page settings."""
        self.page.title = "BizRadar - Business Monitoring"
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.window_min_width = 800
        self.page.window_min_height = 600
        self.page.padding = 0
        self.page.spacing = 0
    
    def build(self):
        """Build and display the application interface."""
        # Initialize views
        self.dashboard_view = DashboardView(self)
        self.settings_view = SettingsView(self)
        self.notifications_view = NotificationsView(self)
        
        # Create navigation rail
        nav_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.icons.DASHBOARD,
                    selected_icon=ft.icons.DASHBOARD,
                    label="Dashboard"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.NOTIFICATIONS,
                    selected_icon=ft.icons.NOTIFICATIONS,
                    label="Notifications"
                ),
                ft.NavigationRailDestination(
                    icon=ft.icons.SETTINGS,
                    selected_icon=ft.icons.SETTINGS,
                    label="Settings"
                ),
            ],
            on_change=self.on_nav_change,
        )
        
        # Create main content area
        self.content_area = ft.Container(
            content=self.dashboard_view.build(),
            expand=True,
            padding=20
        )
        
        # Create app bar
        app_bar = ft.AppBar(
            title=ft.Text("BizRadar", size=20, weight=ft.FontWeight.BOLD),
            bgcolor=ft.colors.BLUE_600,
            color=ft.colors.WHITE,
            actions=[
                ft.IconButton(
                    icon=ft.icons.REFRESH,
                    tooltip="Refresh Data",
                    on_click=self.refresh_data
                ),
                ft.IconButton(
                    icon=ft.icons.INFO,
                    tooltip="About",
                    on_click=self.show_about
                )
            ]
        )
        
        # Main layout
        main_layout = ft.Row(
            controls=[
                nav_rail,
                ft.VerticalDivider(width=1),
                self.content_area
            ],
            expand=True,
            spacing=0
        )
        
        # Add to page
        self.page.appbar = app_bar
        self.page.add(main_layout)
        
        # Check configuration and show setup if needed
        if not self.config.is_configured():
            self.show_setup_dialog()
        
        self.page.update()
    
    def on_nav_change(self, e):
        """Handle navigation rail selection changes."""
        selected_index = e.control.selected_index
        
        if selected_index == 0:  # Dashboard
            self.current_view = "dashboard"
            self.content_area.content = self.dashboard_view.build()
        elif selected_index == 1:  # Notifications
            self.current_view = "notifications"
            self.content_area.content = self.notifications_view.build()
        elif selected_index == 2:  # Settings
            self.current_view = "settings"
            self.content_area.content = self.settings_view.build()
        
        self.page.update()
    
    def refresh_data(self, e):
        """Refresh the current view data."""
        if self.current_view == "dashboard" and self.dashboard_view:
            self.dashboard_view.refresh()
        elif self.current_view == "notifications" and self.notifications_view:
            self.notifications_view.refresh()
        elif self.current_view == "settings" and self.settings_view:
            self.settings_view.refresh()
    
    def show_about(self, e):
        """Show about dialog."""
        app_info = self.config.get_app_info()
        
        dialog = ft.AlertDialog(
            title=ft.Text("About BizRadar"),
            content=ft.Column([
                ft.Text(f"Version: {app_info['version']}"),
                ft.Text(f"Description: {app_info['description']}"),
                ft.Text(f"Status: {'Configured' if app_info['configured'] else 'Not Configured'}"),
                ft.Divider(),
                ft.Text("BizRadar helps business owners monitor their local competitive landscape in real-time using the Foursquare Places API."),
            ], tight=True),
            actions=[
                ft.TextButton("Close", on_click=lambda e: self.close_dialog())
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def show_setup_dialog(self):
        """Show initial setup dialog for API key configuration."""
        api_key_field = ft.TextField(
            label="Foursquare API Key",
            hint_text="Enter your Foursquare Places API key",
            password=True,
            width=400
        )
        
        def save_api_key(e):
            if api_key_field.value:
                if self.config.update_api_key(api_key_field.value):
                    # Reinitialize services with new API key
                    self.foursquare_client = FoursquareClient(api_key_field.value)
                    self.monitoring_service = MonitoringService(self.foursquare_client, self.db_manager)
                    
                    self.close_dialog()
                    self.show_success_message("API key saved successfully!")
                else:
                    self.show_error_message("Failed to save API key. Please try again.")
            else:
                self.show_error_message("Please enter a valid API key.")
        
        dialog = ft.AlertDialog(
            title=ft.Text("Setup Required"),
            content=ft.Column([
                ft.Text("Welcome to BizRadar! To get started, you need to configure your Foursquare API key."),
                ft.Text(""),
                ft.Text("1. Visit https://developer.foursquare.com/"),
                ft.Text("2. Create an account and new app"),
                ft.Text("3. Copy your API key and paste it below:"),
                ft.Text(""),
                api_key_field
            ], tight=True),
            actions=[
                ft.TextButton("Cancel", on_click=lambda e: self.close_dialog()),
                ft.ElevatedButton("Save", on_click=save_api_key)
            ]
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def close_dialog(self):
        """Close the current dialog."""
        if self.page.dialog:
            self.page.dialog.open = False
            self.page.update()
    
    def show_success_message(self, message: str):
        """Show a success snack bar."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.GREEN_600
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_error_message(self, message: str):
        """Show an error snack bar."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.RED_600
        )
        self.page.snack_bar.open = True
        self.page.update()
    
    def show_info_message(self, message: str):
        """Show an info snack bar."""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.colors.BLUE_600
        )
        self.page.snack_bar.open = True
        self.page.update()
